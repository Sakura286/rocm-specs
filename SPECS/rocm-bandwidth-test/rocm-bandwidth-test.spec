# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstreamname rocm_bandwidth_test
%global rocm_release 7.2
%global rocm_patch 4
%global rocm_version %{rocm_release}.%{rocm_patch}

# GPU HW is required to run %check, and needs to run locally
%bcond check 0

Name:           rocm-bandwidth-test
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Bandwidth test for ROCm
# License mismatch
# https://github.com/ROCm/rocm_bandwidth_test/issues/127
License:        NCSA AND MIT
URL:            https://github.com/ROCm/rocm_bandwidth_test
#!RemoteAsset:  sha256:abba532eeb43f0740ed9bbacc39ff738a55acae0f01ba5d75a899e313ddc35ea
Source0:        %{url}/archive/06dd9df114855ed2dc38cd731ad214066a62d6da/rocm_bandwidth_test-06dd9df114855ed2dc38cd731ad214066a62d6da.tar.gz
# From base_test.cpp
Source1:        LICENSE.NCSA.txt
BuildSystem:    cmake

# No therock-10.1 release exists for this standalone tool; use latest tagged source.
BuildOption(prep):  -n rocm_bandwidth_test-06dd9df114855ed2dc38cd731ad214066a62d6da

BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  rocr-runtime-devel >= 10.1.0

%description
ROCm Bandwidth Test is designed to capture the performance
characteristics of buffer copying and kernel read and write
operations. The benchmark help screen shows various options
for initiating copy, read, and write operations. In
addition to this, you can also query the system topology in
terms of memory pools and their agents.

%prep -a
# Remove execute permissions on docs
# https://github.com/ROCm/rocm_bandwidth_test/issues/128
chmod a-x LICENSE.txt
chmod a-x README.md
chmod a-x ROCmBandwithTest_UserGuide.pdf
cp %{SOURCE1} .

%install -a
rm -f %{buildroot}%{_prefix}/share/doc/rocm-bandwidth-test/LICENSE.txt

%check
%if %{with check}
%{_vpath_builddir}/rocm-bandwidth-test
# On a gfx1201, the start should look something like
#          RocmBandwidthTest Version: 2.6.0
#
#          Launch Command is: redhat-linux-build/rocm-bandwidth-test (rocm_bandwidth -a + rocm_bandwidth -A)
#
#
#          Device: 0,  Intel(R) Core(TM) i5-10400 CPU @ 2.90GHz
#          Device: 1,  AMD Radeon Graphics,  GPU-7b2a57bc7a036a5f,  03:0.0
# ...
%endif

%files
%doc README.md ROCmBandwithTest_UserGuide.pdf
%license LICENSE.txt LICENSE.NCSA.txt
%{_bindir}/rocm-bandwidth-test

%changelog
%autochangelog
