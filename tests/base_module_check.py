from sage.context import Severity


def get_major_issues(file_analysis):
    return file_analysis.violations[Severity.major.name]


def get_minor_issues(file_analysis):
    return file_analysis.violations[Severity.minor.name]


def get_info_issues(file_analysis):
    return file_analysis.violations[Severity.info.name]


def get_num_of_issues(file_analysis):
    return len(file_analysis.violations[Severity.major.name]) + \
           len(file_analysis.violations[Severity.minor.name]) + \
           len(file_analysis.violations[Severity.info.name])
