from typing import List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class BenchmarkArgs:
    args: List[str]
    stdin: Optional[str] = None

    def __iter__(self):
        return iter((self.args, self.stdin))

class BenchmarkSuite(ABC): 
    @abstractmethod
    def get_workload_spec(self, name: str, idx: int) -> (str, BenchmarkArgs):
        pass
    
    @abstractmethod
    def get_benchmark_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_num_workloads(self) -> int:
        pass
