import io
import json
import logging
import tempfile

import netCDF4 as nc
import numpy as np
from PIL import Image
from wcps.model import WCPSClientException
from wcps.service import Service as WCPSConnection, WCPSResult, WCPSResultType
from wcs.service import WebCoverageService

from src.timer import Timer
from src.wcps_crash_course import WCPS_CRASH_COURSE, WCPS_UDFS

logger = logging.getLogger()
SAVE_THRESHOLD = 1000


class RasdamanActions:
    """Handle communication with rasdaman and return LLM-appropriate responses."""

    def __init__(self, rasdaman_url, username, password):
        self.rasdaman_url = rasdaman_url
        self.username = username
        self.password = password
        self.wcs_service = WebCoverageService(rasdaman_url, username=username, password=password)
        self.wcps_service = WCPSConnection(rasdaman_url, username=username, password=password)

    def list_coverages_action(self) -> str:
        """
        Lists all available datacubes (coverages) in the rasdaman database.
        """
        logger.info("Listing coverages in rasdaman...")
        with Timer() as timer:
            coverages = self.wcs_service.list_coverages()
            coverages_str = ', '.join(coverages.keys())
            total_cov_count = len(coverages)
            ret = f'{total_cov_count} coverages (datacubes) are available: {coverages_str}'
            udfs_str = self.wcps_service.list_udfs()
            if udfs_str:
                try:
                    udfs_json = json.loads(udfs_str)
                    # convert json into concise text, e.g. from
                    # {
                    #     "namespace" : "example",
                    #     "name" : "Avg2",
                    #     "parameters" : [ "Coverage" ],
                    #     "returns" : "Number",
                    #     "documentation" : "Calculate the average of a coverage expression."
                    # }
                    # to 
                    # - example.Avg2(Coverage) -> Number: Calculate the average of a coverage expression.
                    # 
                    total_udf_count = len(udfs_json)
                    output = ["{total_udf_count} UDFs (user-defined functions) are available:"]
                    for udf in udfs_json:
                        params = ", ".join(udf['parameters'])
                        func = f"{udf['namespace']}.{udf['name']}"
                        line = f"- {func}({params}) -> {udf['returns']} : {udf['documentation']}"
                        output.append(line)
                    
                    ret += "\n\n"
                    ret += "\n".join(output)
                except:
                    pass
            timer.log(f"Listed {total_cov_count} coverages")
        return ret

    def describe_coverage_action(self, coverage_id: str) -> str:
        """
        Retrieves structural metadata for a specific datacube.
        """
        logger.info(f"Describing coverage: {coverage_id}")
        with Timer() as timer:
            full_cov = self.wcs_service.list_full_info(coverage_id)
            ret = full_cov.to_short_str()
            timer.log(f"Done getting description for {coverage_id}")
        return ret

    def wcps_query_crash_course_action(self) -> str:
        """
        Returns a crash course on writing WCPS queries.
        """
        logger.info("Returning WCPS crash course.")
        ret = WCPS_CRASH_COURSE
        try:
            # inject UDFs doc if the service has an UDFs available
            if self.wcps_service.list_udfs():
                before_header = '## LLM Generation Checklist'
                new_section = f'{WCPS_UDFS}\n\n{before_header}'
                ret = ret.replace(before_header, new_section)
        except:
            pass
        return ret

    def execute_wcps_query_action(self, wcps_query: str) -> dict:
        """
        Executes a WCPS query in rasdaman using the wcps-python-client library.
        Returns a structured dictionary with result type, file path (if applicable),
        and metadata.
        """
        logger.info(f"Executing WCPS query: {wcps_query}")

        # 1. execute the WCPS query
        try:
            with Timer() as timer:
                response: WCPSResult = self.wcps_service.execute(wcps_query)
                timer.log("Executed WCPS query")
        except WCPSClientException as e:
            logger.error(f"Executing WCPS query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": wcps_query,
            }

        # 2. interpret the result in order to return a structured response
        result = {
            "success": True,
            "query": wcps_query,
            "result_type": response.type.name,
        }

        try:
            # scalars: returned directly
            if response.type in [WCPSResultType.SCALAR, WCPSResultType.MULTIBAND_SCALAR]:
                result["value"] = response.value
                logger.info(f"Returning scalar result: {response.value}")
                return result

            # JSON: return result < SAVE_THRESHOLD as value, otherwise save as temp file
            if response.type == WCPSResultType.JSON:
                json_str = json.dumps(response.value)
                if len(json_str) < SAVE_THRESHOLD:
                    result["value"] = response.value
                    logger.info(f"Returning JSON result: {json_str}")
                    return result

                # else result is too large, save as file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmpfile:
                    tmpfile.write(json_str)
                    result["file_path"] = tmpfile.name
                    result["file_size"] = str(len(json_str))
                    logger.info(f"JSON result saved in file {tmpfile.name}")
                    return result

            # at this point the result is some binary format -> save to a file first
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmpfile:
                tmpfile.write(response.value)
                result["file_path"] = tmpfile.name
                result["file_size"] = str(len(response.value))

            # 2D images: add image metadata
            if response.type == WCPSResultType.IMAGE:
                img = Image.open(io.BytesIO(response.value))
                width, height = img.size
                result["metadata"] = {
                    "width": width,
                    "height": height,
                    "bands": len(img.getbands()),
                    "dtype": str(np.array(img).dtype),
                }
                logger.info(f"Image result: {width}x{height} pixels, {len(img.getbands())} bands")
                return result

            # NetCDF: add metadata
            if response.type == WCPSResultType.NETCDF:
                with nc.Dataset("memory", mode="r", memory=response.value) as ds:  # pylint: disable=no-member
                    dimensions = {name: len(dim) for name, dim in ds.dimensions.items()}
                    variables = {}
                    for var_name, var in ds.variables.items():
                        if var_name in ds.dimensions:
                            continue
                        variables[var_name] = {
                            "dims": var.dimensions,
                            "shape": var.shape,
                            "type": str(var.dtype),
                            "attributes": dict(var.__dict__),
                        }
                    result["metadata"] = {
                        "dims": dimensions,
                        "vars": variables,
                    }
                logger.info(f"NetCDF result: dimensions={dimensions}, variables={list(variables.keys())}")
                return result

            # Non-encoded raw array (NUMPY or other binary types)
            logger.info(f"Binary result saved in file {result['file_path']}")
            return result

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed handling WCPS query result: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
