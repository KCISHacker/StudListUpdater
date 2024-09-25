if __name__ == "__main__":
    print("Hello from 华东康桥学武系统 - kcisinfo module")
    exit()

from .functions import get_info
from .functions import get_name_ordering
from .functions import get_password
from .functions import get_card
from .functions import replace_printed_line
from .functions import get_student_info
from .functions import to_student_info_dict

__all__ = ['get_info', 'get_name_ordering', 'get_password', 'get_card', 'replace_printed_line', 'get_student_info', 'to_student_info_dict']