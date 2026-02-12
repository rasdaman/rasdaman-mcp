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
from src.wcps_crash_course import WCPS_CRASH_COURSE

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

    def list_coverages_action(self) -> list[str]:
        """
        Lists all available datacubes (coverages) in the rasdaman database.
        """
        logger.info("Listing coverages in rasdaman...")
        with Timer() as timer:
            coverages = self.wcs_service.list_coverages()
            ret = list(coverages.keys())
            timer.log(f"Listed {len(coverages)} coverages")
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
        return WCPS_CRASH_COURSE

    def execute_wcps_query_action(self, wcps_query: str) -> str:
        """
        Executes a WCPS query in rasdaman using the wcps-python-client library.
        """
        logger.info(f"Executing WCPS query: {wcps_query}")

        # 1. execute the WCPS query
        try:
            with Timer() as timer:
                response: WCPSResult = self.wcps_service.execute(wcps_query)
                timer.log("Executed WCPS query")
        except WCPSClientException as e:
            ret = f"Executing WCPS query failed: {e}"
            logger.error(ret)
            return ret

        # 2. interpret the result in order to return a more meaningful response to the LLM
        try:
            # scalars: returned directly
            if response.type in [WCPSResultType.SCALAR, WCPSResultType.MULTIBAND_SCALAR]:
                ret = str(response.value)
                logger.info(f"Returning scalar result: {ret}")
                return ret

            # JSON: return result < SAVE_THRESHOLD as string, otherwise save as temp file
            if response.type == WCPSResultType.JSON:
                ret = json.dumps(response.value)
                if len(ret) < SAVE_THRESHOLD:
                    logger.info(f"Returning JSON result: {ret}")
                    return ret

                # else result is too large, save as file and return first 500 chars
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpfile:
                    tmpfile.write(ret)
                    ret = f"JSON result saved in file {tmpfile.name}"
                    logger.info(ret)
                    return ret

            # at this point the result is some binary format -> save to a file first
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmpfile:
                tmpfile.write(response.value)
                ret = f"{response.type.capitalize()} result saved in "
                ret += f"file {tmpfile.name} of size {len(response.value)} bytes; "

            # 2D images: return filepath + image metadata
            if response.type == WCPSResultType.IMAGE:
                img = Image.open(io.BytesIO(response.value))
                width, height = img.size
                ret += f"the result is an image of {width} x {height} pixels, "
                ret += f"{len(img.getbands())} bands of type {np.array(img).dtype}."
                logger.info(ret)
                return ret

            # NetCDF: return filepath + image metadata
            if response.type == WCPSResultType.NETCDF:
                with nc.Dataset("memory", mode="r", memory=response.value) as ds:  # pylint: disable=no-member
                    dimensions = {name: len(dim) for name, dim in ds.dimensions.items()}
                    variables = {}
                    for var_name, var in ds.variables.items():
                        if var_name in ds.dimensions:
                            continue
                        variables[var_name] = {
                            "type": var.dtype,
                            "shape": var.shape,
                            "dimensions": var.dimensions,
                            "attributes": dict(var.__dict__),
                        }
                    ret += f"dimensions: {dimensions}; variables: {variables}"
                logger.info(ret)
                return ret

            # Non-encoded raw array
            logger.info(ret)
            return ret

        except Exception as e:  # pylint: disable=broad-exception-caught
            ret = f"Failed handling WCPS query result: {e}"
            logger.error(ret)
            return ret
