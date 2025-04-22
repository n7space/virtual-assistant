from typing import List, Set, Dict
import json
import logging
import openpyxl


class Requirement:
    id: str
    type: str
    validation_type: str
    description: str
    note: str
    justification: str
    traces: List[str]

    def __init__(self, id: str = "", description: str = "") -> None:
        self.id = id
        self.type = None
        self.validation_type = None
        self.description = description
        self.note = None
        self.justification = None
        self.traces = []


class Mappings:
    worksheet_name: str
    first_row_number: int
    id: str
    type: str
    validation_type: str
    description: str
    note: str
    justification: str
    traces: str
    trace_separator: str

    def __init__(self) -> None:
        # Column mappings based on MBEP-KISPE-EP-SRS-001 v1.0
        self.worksheet_name = "5. Requirements"
        self.first_row_number = 3
        self.id = "A"
        self.type = "B"
        self.validation_type = "I"
        self.description = "C"
        self.note = "G"
        self.justification = "E"
        self.traces = "D"
        self.trace_separator = ","

    def update_from_dict(self, dict: Dict) -> "Mappings":
        self.worksheet_name = dict.get("worksheet_name", self.worksheet_name)
        self.first_row_number = dict.get("first_row_number", self.first_row_number)
        self.id = dict.get("id", self.id)
        self.type = dict.get("type", self.type)
        self.validation_type = dict.get("validation_type", self.validation_type)
        self.description = dict.get("description", self.description)
        self.note = dict.get("note", self.note)
        self.justification = dict.get("justification", self.justification)
        self.traces = dict.get("traces", self.traces)
        self.trace_separator = dict.get("trace_separator", self.trace_separator)
        return self


class VaRequirementReader:
    __mappings: Mappings

    def __init__(self, mappings: Mappings = None) -> None:
        self.__mappings = mappings if mappings is not None else Mappings()

    # openpyxl is not very well typed
    def __read_value(self, sheet, mapping: str, index: int):
        # Let's use key notation instead of indexing, e.g., "B12", as it is more human readable
        key = mapping + str(index)
        value = sheet[key].value
        logging.debug(f"Reading values {key} -> {value}")
        return value

    def read_requirements(self, file_name: str) -> List[Requirement]:
        result = []
        wb = openpyxl.load_workbook(file_name)
        sheet = wb[self.__mappings.worksheet_name]
        for row in range(self.__mappings.first_row_number, sheet.max_row + 1):
            requirement = Requirement()
            requirement.id = self.__read_value(sheet, self.__mappings.id, row)
            requirement.type = self.__read_value(sheet, self.__mappings.type, row)
            requirement.validation_type = self.__read_value(
                sheet, self.__mappings.validation_type, row
            )
            requirement.description = self.__read_value(
                sheet, self.__mappings.description, row
            )
            requirement.note = self.__read_value(sheet, self.__mappings.note, row)
            requirement.justification = self.__read_value(
                sheet, self.__mappings.justification, row
            )
            requirement.traces = self.__read_value(sheet, self.__mappings.traces, row)
            if requirement.traces is not None:
                requirement.traces = requirement.traces.split(
                    self.__mappings.trace_separator
                )
            else:
                requirement.traces = []
            result.append(requirement)
        return result
