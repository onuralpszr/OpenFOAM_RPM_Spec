#
# Spec file for package openfoam-selector
#
# Copyright (c) 2018-2020 OpenCFD Ltd. (www.openfoam.com)
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself.
# The license of the pristine package is BSD-3-Clause.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
# ------------------

Name:           openfoam-selector
Version: 1.0.6
Release: 1
Url:            http://www.openfoam.com
Summary:        Tool to manage which OpenFOAM version to use
License:        BSD-3-Clause
Source0:        https://sourceforge.net/projects/openfoam/files/utils/%{name}-%{version}.tgz
BuildArch:      noarch
BuildRequires:  automake autoconf make perl

%if 0%{?suse_version}
Group:          System/Console
%{perl_requires}
%endif


%description
A simple tool that allows system administrators or users to set a site-wide
default for which OpenFOAM version is to be used, but also allow
users to set their own preferred OpenFOAM version, thereby overriding
the site-wide default.

The default can be changed easily via the openfoam-selector command --
editing of shell startup files is not required.

%prep
%setup -q

%build
%configure --with-shell-startup-dir=%{_sysconfdir}/profile.d
make

%install
make DESTDIR=%{buildroot} install

%files
%doc README* LICENSE
%{_bindir}/openfoam-selector
%{_bindir}/openfoam-selector-menu
%{_mandir}/man1/openfoam-selector.*
%{_mandir}/man1/openfoam-selector-menu.*
%config %attr(644,root,root) %{_sysconfdir}/profile.d/*

%changelog