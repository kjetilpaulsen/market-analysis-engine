from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectIdentity:
    # This is the package/distribution name in packaging metadata.
    dist_name: str
    # This is the user-facing CLI/app identity
    app_name: str
    # This is the package name
    package_name: str
    # This is the logger namespace
    logger_name: str


IDENTITY = ProjectIdentity(
    dist_name="market-analysis-engine",
    app_name="market-analysis-engine",
    package_name="market_analysis_engine",
    logger_name="market_analysis_engine",
)
