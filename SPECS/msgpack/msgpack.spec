# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           msgpack
Version:        3.1.0
Release:        %autorelease
Summary:        Binary-based efficient object serialization library
License:        BSL-1.0
URL:            http://msgpack.org
#!RemoteAsset
Source0:        https://github.com/msgpack/msgpack-c/releases/download/cpp-%{version}/%{name}-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DCMAKE_POLICY_VERSION_MINIMUM=3.5

# https://github.com/msgpack/msgpack-c/commit/53d2ea9ad3cc20e1beac2e1c014082c25e221182
Patch0:         0001-Fixed-724.patch
Patch1:         0002-msgpack-cmake4.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  doxygen
# for %%check
BuildRequires:  pkgconfig(gtest)
BuildRequires:  pkgconfig(zlib)

%description
MessagePack is a binary-based efficient object serialization
library. It enables to exchange structured objects between many
languages like JSON. But unlike JSON, it is very fast and small.

%package        devel
Summary:        Libraries and header files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Libraries and header files for %{name}

%prep -a
# gtest 1.17.0 requires at least C++17
sed -i "s|-std=c++98|-std=gnu++17|g" CMakeLists.txt

%check -p
# https://github.com/msgpack/msgpack-c/issues/697
export GTEST_FILTER=-object_with_zone.ext_empty

%files
%license LICENSE_1_0.txt COPYING
%doc AUTHORS ChangeLog NOTICE README README.md
%{_libdir}/*.so.*

%files devel
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/msgpack.pc
%{_libdir}/cmake/msgpack

%changelog
%autochangelog
