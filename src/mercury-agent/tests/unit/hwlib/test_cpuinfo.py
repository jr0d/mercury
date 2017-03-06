# Copyright 2017 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""Module to unit test mercury.inspector.hwlib.cpuinfo"""

import mock
import pytest

import mercury.inspector.hwlib.cpuinfo as cpuinfo
from tests.unit.base import MercuryAgentUnitTest


EXAMPLE_PROC_CPUINFO_OUTPUT = """processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1268.115
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 0
cpu cores	: 6
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6612.06
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:


processor	: 1
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1199.835
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 1
cpu cores	: 6
apicid		: 2
initial apicid	: 2
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6615.66
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 2
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.036
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 2
cpu cores	: 6
apicid		: 4
initial apicid	: 4
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.18
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 3
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.036
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 3
cpu cores	: 6
apicid		: 6
initial apicid	: 6
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.25
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 4
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.640
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 4
cpu cores	: 6
apicid		: 8
initial apicid	: 8
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.27
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 5
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.439
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 5
cpu cores	: 6
apicid		: 10
initial apicid	: 10
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.28
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 6
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1300.543
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 0
cpu cores	: 6
apicid		: 1
initial apicid	: 1
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6618.23
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 7
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.439
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 1
cpu cores	: 6
apicid		: 3
initial apicid	: 3
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.75
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 8
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.439
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 2
cpu cores	: 6
apicid		: 5
initial apicid	: 5
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.36
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 9
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.036
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 3
cpu cores	: 6
apicid		: 7
initial apicid	: 7
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.22
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 10
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1199.835
cache size	: 15360 KB
physical id	: 0
siblings	: 12
core id		: 4
cpu cores	: 6
apicid		: 9
initial apicid	: 9
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs		:
bogomips	: 6616.40
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor       : 11
vendor_id       : GenuineIntel
cpu family      : 6
model           : 63
model name      : Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping        : 2
microcode       : 0x39
cpu MHz         : 1201.245
cache size      : 15360 KB
physical id     : 0
siblings        : 12
core id         : 5
cpu cores       : 6
apicid          : 11
initial apicid  : 11
fpu             : yes
fpu_exception   : yes
cpuid level     : 15
wp              : yes
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts
bugs            :
bogomips        : 6616.29
clflush size    : 64
cache_alignment : 64
address sizes   : 46 bits physical, 48 bits virtual
power management:

"""

CPUINFO_TEMPLATE_SINGLE_CPU_ENTRY = """processor	: %(processor_num)s
vendor_id	: GenuineIntel
cpu family	: 6
model		: 63
model name	: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz
stepping	: 2
microcode	: 0x39
cpu MHz		: 1200.640
cache size	: 15360 KB
physical id	: %(physical_id)s
siblings	: %(siblings)s
core id		: %(core_id)s
cpu cores	: %(cpu_cores)s
apicid		: %(apic_id)s
initial apicid	: %(apic_id)s
fpu		: yes
fpu_exception	: yes
cpuid level	: 15
wp		: yes
flags		: %(flags)s
bugs		:
bogomips	: 6616.29
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

"""

DEFAULT_CPU_FLAGS = "fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts"


def get_fake_cpuinfo_output(num_logical_processors=2,
                            hyper_threaded=False,
                            flags=DEFAULT_CPU_FLAGS):
    """Generates valid-looking cpuinfo output for testing."""
    fake_output = ''
    cpu_cores = (num_logical_processors / 2) if hyper_threaded else \
        num_logical_processors
    for proc_num in range(0, num_logical_processors):
        fake_output += CPUINFO_TEMPLATE_SINGLE_CPU_ENTRY % {
            'processor_num': proc_num,
            'physical_id': 0,
            'siblings': num_logical_processors,
            'core_id': (proc_num % 2) if hyper_threaded else proc_num,
            'cpu_cores': cpu_cores,
            'apic_id': proc_num,
            'flags': flags
        }
    return fake_output


class MercuryHwlibCpuinfoUnitTests(MercuryAgentUnitTest):
    """Unit tests for mercury.inspector.hwlib.cpuinfo"""
    @mock.patch("mercury.inspector.hwlib.cpuinfo.os.path.exists")
    @mock.patch("mercury.inspector.hwlib.cpuinfo.open")
    def setUp(self, open_mock, os_path_exists_mock):
        """Setup a CPUInfo object to use for further tests."""
        super(MercuryHwlibCpuinfoUnitTests, self).setUp()
        os_path_exists_mock.return_value = True
        open_mock.return_value.__enter__.return_value.read.return_value = \
            EXAMPLE_PROC_CPUINFO_OUTPUT
        self.cpuinfo_obj = cpuinfo.CPUInfo()

    @mock.patch("mercury.inspector.hwlib.cpuinfo.os.path.exists")
    def test_proc_cpuinfo_absent(self, os_path_exists_mock):
        """Test what happens if /proc/cpuinfo doesn't exist.

        Particularly when constrcuting a CPUInfo object.
        """
        os_path_exists_mock.return_value = False
        with pytest.raises(OSError):
            cpuinfo.CPUInfo()

    def test_cpu_info_example_output(self):
        """Look at various properties of cpuinfo object to check sanity.

        Tests against EXAMPLE_PROC_CPUINFO_OUTPUT, which is cpuinfo output
        for a 5820k (6 physical cores, 12 logical ones).
        """
        cores_zero = self.cpuinfo_obj.get_cores(0)
        assert isinstance(cores_zero, list)
        assert len(cores_zero) == 12
        for core in cores_zero:
            assert isinstance(core, dict)

        assert self.cpuinfo_obj.processor_ids == list(range(0, 12))
        assert self.cpuinfo_obj.logical_core_count == 12
        assert self.cpuinfo_obj.total_physical_core_count == 6
        assert self.cpuinfo_obj.cores_per_processor == 6

        lpi = self.cpuinfo_obj.logical_processor_index
        assert isinstance(lpi, dict)
        assert len(lpi.keys()) == 12
        assert list(lpi.keys()) == list(range(0, 12))

        core_zi = self.cpuinfo_obj.core_zero_index
        assert isinstance(core_zi, dict)
        assert len(core_zi.keys()) == 1

    def test_core_dict_missing_phys_id(self):
        """Test behavior when a core_dict is missing data."""
        del self.cpuinfo_obj.core_dicts[0]['physical_id']
        result = self.cpuinfo_obj.physical_index
        assert isinstance(result, dict)
        assert len(result.keys()) == 1

    @mock.patch("mercury.inspector.hwlib.cpuinfo.os.path.exists")
    @mock.patch("mercury.inspector.hwlib.cpuinfo.open")
    def test_get_cpufreq_info(self, open_mock, os_path_exists_mock):
        """Test get_cpufreq_info()."""
        # Test normal, expected operation.
        os_path_exists_mock.return_value = True
        open_mock.return_value.__enter__.return_value.read.side_effect = [
            "1200000", "4000000", "2000000"]

        result = cpuinfo.get_cpufreq_info("0")

        cpufreq_address = '/sys/devices/system/cpu/cpu0/cpufreq'
        assert os_path_exists_mock.called
        os_path_exists_mock.assert_called_with(cpufreq_address)
        open_mock.assert_has_calls([
            mock.call(cpufreq_address + '/scaling_min_freq'),
            mock.call(cpufreq_address + '/scaling_max_freq'),
            mock.call(cpufreq_address + '/scaling_cur_freq')], any_order=True)

        assert isinstance(result, dict)
        assert len(result.keys()) == 3
        assert result['min'] == 1200000
        assert result['max'] == 4000000
        assert result['cur'] == 2000000

        # See what happens if the sys cpu path doesn't exist.
        os_path_exists_mock.return_value = False
        result = cpuinfo.get_cpufreq_info("0")
        assert result == {}

    @mock.patch("mercury.inspector.hwlib.cpuinfo.get_cpufreq_info")
    def test_get_speed_info(self, cpufreq_info_mock):
        """Test CPUInfo.get_physical_speed_info() operation."""
        cpufreq_info_mock.side_effect = [
            {'min': 1200000, 'max': 4000000, 'cur': 2000000}] * 12
        speed_info = self.cpuinfo_obj.get_physical_speed_info()
        assert isinstance(speed_info, list)
        assert len(speed_info) == 1
        assert speed_info[0]['cpufreq_enabled'] == True
        assert speed_info[0]['bogomips'] == 6612.06
        assert speed_info[0]['current'] == 2000000.00
        assert speed_info[0]['min'] == 1200000.00
        assert speed_info[0]['max'] == 4000000.00

        # See what happens when cpufreq is not available.
        cpufreq_info_mock.side_effect = [False]
        speed_info = self.cpuinfo_obj.get_physical_speed_info()
        assert isinstance(speed_info, list)
        assert len(speed_info) == 1
        assert speed_info[0]['cpufreq_enabled'] == False
        assert speed_info[0]['bogomips'] == 6612.06
        assert speed_info[0]['current'] == 1268.115
        assert speed_info[0]['min'] == 1268.115
        assert speed_info[0]['max'] == 1268.115
