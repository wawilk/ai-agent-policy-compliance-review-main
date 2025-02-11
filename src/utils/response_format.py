from semantic_kernel.kernel_pydantic import KernelBaseModel

class RuleViolation(KernelBaseModel):
    rule_name: str
    text: str
    explanation: str

class Section(KernelBaseModel):
    name: str
    rule_violations: list[RuleViolation]

class PolicyComplianceReport(KernelBaseModel):
    compliant: bool
    sections: list[Section]