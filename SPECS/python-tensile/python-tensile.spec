# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tensile
%global upstreamname Tensile
%global rocm_version 7.1.1

Name:           python-%{srcname}
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Tool for creating benchmark-driven backend libraries for GEMMs
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
Source0:        %{url}/releases/download/rocm-%{rocm_version}/tensile.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l %{upstreamname}

Patch0:         0001-tensile-set-default-paths.patch

BuildRequires:  python3-devel
BuildRequires:  python3dist(installer)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Requires:       cmake-filesystem
Requires:       hipcc
Requires:       rocminfo
Requires:       python3dist(msgpack)
Requires:       python3dist(pyyaml)

Provides:       python3-%{srcname}
%python_provide python3-%{srcname}

%description
Tensile is a tool for creating benchmark-driven backend libraries for GEMMs,
GEMM-like problems (such as batched GEMM), and general N-dimensional tensor
contractions on a GPU. The Tensile library is mainly used as backend library to
rocBLAS. Tensile acts as the performance backbone for a wide variety of
'compute' applications running on AMD GPUs.

%prep -a
#Fix a few things:
chmod 755 Tensile/Configs/miopen/convert_cfg.py
sed -i -e 's@bin/python@bin/python3@' Tensile/Configs/miopen/convert_cfg.py
sed -i -e 's@bin/python@bin/python3@' Tensile/Tests/create_tests.py
sed -i -e 's@bin/env python3@bin/python3@' Tensile/bin/Tensile
sed -i -e 's@bin/env python3@bin/python3@' Tensile/bin/TensileCreateLibrary

# hack where TensileGetPath is located
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g' Tensile/cmake/TensileConfig.cmake

# Ignora asm cap
sed -i -e 's@globalParameters["IgnoreAsmCapCache"] = False@globalParameters["IgnoreAsmCapCache"] = True@' Tensile/Common.py
sed -i -e 's@arguments["IgnoreAsmCapCache"] = args.IgnoreAsmCapCache@arguments["IgnoreAsmCapCache"] = True@' Tensile/TensileCreateLibrary.py
sed -i -e 's@if not ignoreCacheCheck and derivedAsmCaps@if False and derivedAsmCaps@' Tensile/Common.py

# Reduce requirements
sed -i -e '/joblib/d' requirements.*
sed -i -e '/rich/d' requirements.*
sed -i -e '/msgpack/d' requirements.*

# No amdclang when build rocm-llvm as component
sed -i 's@AssemblerPath"] = None@AssemblerPath"] = "clang++"@g' Tensile/Common.py
sed -i 's@CxxCompiler"] = "amdclang++"@CxxCompiler"] = "hipcc"@g' Tensile/Common.py
sed -i 's@ASSEMBLER = osSelect(linux="amdclang++"@ASSEMBLER = osSelect(linux="clang++"@g' Tensile/Utilities/Toolchain.py
sed -i 's@CXX_COMPILER = osSelect(linux="amdclang++"@CXX_COMPILER = osSelect(linux="hipcc"@g' Tensile/Utilities/Toolchain.py
sed -i 's@amdclang@clang@g' Tensile/Common.py Tensile/Utilities/Toolchain.py

# Use /usr instead of /opt/rocm for prefix
sed -i "s@opt/rocm/hip@usr@g" Tensile/Tests/hipModuleLoad_timing/Makefile
sed -i "s@opt/rocm@usr@g" \
    Tensile/Common.py \
    Tensile/Source/CMakeLists.txt \
    Tensile/Source/FindHIP.cmake \
    Tensile/Source/cmake/FindROCmSMI.cmake \
    Tensile/Source/cmake/FindROCmSMI.cmake \
    Tensile/Utilities/Toolchain.py
sed -i "s@llvm/bin@bin@g" Tensile/Utilities/Toolchain.py

%generate_buildrequires
%pyproject_buildrequires

%install -a
# /usr/cmake/* -> /usr/lib/cmake/Tensile
mkdir -p %{buildroot}%{_datadir}/cmake/Tensile
mv %{buildroot}%{_prefix}/cmake/* %{buildroot}%{_datadir}/cmake/Tensile/
rm -rf %{buildroot}%{_prefix}/cmake

# Do not distribute broken bins
rm %{buildroot}%{_bindir}/tensile*

# rm hard links and replace
rm %{buildroot}%{python3_sitelib}/%{upstreamname}/cmake/*.cmake
mv %{buildroot}%{_datadir}/cmake/Tensile/*.cmake %{buildroot}%{python3_sitelib}/%{upstreamname}/cmake/

%pyproject_save_files %{upstreamname}

%check
# tensile requires GPU hardware at runtime
# optional dependencies (joblib) are intentionally excluded

find %{buildroot}

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.md
# Do not distribute tests
%exclude %{python3_sitelib}/%{upstreamname}/Tests
%{_bindir}/Tensile
%{_bindir}/TensileBenchmarkCluster
%{_bindir}/TensileCreateLibrary
%{_bindir}/TensileGetPath
%{_bindir}/TensileRetuneLibrary

%changelog
%{?autochangelog}
