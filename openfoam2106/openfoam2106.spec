#
# Spec file for package openfoam
#
# Copyright (c) 2018-2021 OpenCFD Ltd. (www.openfoam.com)
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself.
# The license of the pristine package is GPL-3.0-or-later.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
# ------------------

%define foam_api 2106
%define foam_patch    1
%define full_version  %{foam_api}.%{foam_patch}

# OpenFOAM uses YYMMDD for patch versions, no special tar-file for anything smaller
%if 0%{?foam_patch} > 1000
%define tar_filename  OpenFOAM-v%{foam_api}_%{foam_patch}.tgz
%else
%define tar_filename  OpenFOAM-v%{foam_api}.tgz
%endif

# Enable scotch, ptscotch by default
%bcond_without metis
%bcond_without scotch
%bcond_without ptscotch

# Enable openfoam-selector for openSUSE (part of the science repo)
%if 0%{?suse_version}
 %bcond_without foam_selector
%else
 %bcond_with    foam_selector
%endif


# Basic hpc build - currently only openmpi
%global mpi_family openmpi

%if 0%{?sle_version} >= 150200
%define mpi_vers 2
%else
%define mpi_vers 1
%endif

# "openmpi1" was "openmpi" in Leap 15.x/SLE15
%if 0%{?suse_version} >= 1550 || "%{mpi_family}" != "openmpi"  || "%{mpi_vers}" != "1"
%define mpi_ext %{?mpi_vers}
%endif

# ------------------
# SLE: cgal does not exist, or hard to find
# SLE: scotch packaged as gnu-xxx-hpc
# RedHat: cgal seems to be a problem

%if !0%{?is_opensuse} && 0%{?sle_version}
%bcond_with cgal
%bcond_without hpc
%define hpc_mpi_package gnu-%{mpi_family}%{?mpi_vers}-hpc
%else
%bcond_with hpc
  %if 0%{?fedora}%{?suse_version}
%bcond_with cgal
  %else
%bcond_with cgal
  %endif
%endif
# ------------------

Name:           openfoam%{foam_api}
Version:        %{full_version}
Release:        210910%{?dist}
Url:            http://www.openfoam.com
Summary:        Free, Open Source, Computational Fluid Dynamics Package
License:        GPLv3+
Source0:        https://sourceforge.net/projects/openfoam/files/v%{foam_api}/%{tar_filename}
Source1:        openfoam-rpmlintrc
Prefix:         /usr/lib/openfoam
Provides:       com.openfoam = %{foam_api}
Requires:       %{name}-common

# Original project directory (in tar file)
%define projectTarDir OpenFOAM-v%{foam_api}

# Installation directory name
%define projectDir openfoam%{foam_api}

# Shell session (wrapper) script
%define shell_session %{_bindir}/openfoam%{foam_api}

# Installers
%define dirInstaller bin/tools/install-dirs
%define binInstaller bin/tools/install-platform


%if 0%{?rhel}
# Need this for /etc/profile.d/modules.sh
Requires:       environment-modules
%endif
%if 0%{?fedora}%{?rhel}
Requires:       environment(modules)
%if !0%{?el7}
BuildRequires:  rpm-mpi-hooks
%endif
%endif
BuildRequires:  %{mpi_family}%{?mpi_ext}-devel
Requires:       %{mpi_family}%{?mpi_ext}

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  flex
BuildRequires:  make
BuildRequires:  m4
BuildRequires:  binutils
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel
BuildRequires:  readline-devel
BuildRequires:  boost-devel
BuildRequires:  fftw3-devel
%if %{with scotch} && !%{with hpc}
BuildRequires:  scotch-devel
  %if 0%{?fedora}%{?rhel}
Requires:       scotch
  %else
Requires:       libscotch0
  %endif
%endif
# This needs better sorting out
# - openSUSE (non-hpc):
#   ptscotch-openmpi2-devel, libptscotch0-openmpi2
# - SUSE (-hpc):
#   ptscotch-gnu-openmpi2-hpc-devel, libptscotch-gnu-openmpi2-hpc
# - RedHat
#   ptscotch-openmpi2-devel, libptscotch-openmpi2
%if %{with ptscotch}
  %if %{with hpc}
BuildRequires:  ptscotch-%{hpc_mpi_package}-devel
Requires:       libptscotch-%{hpc_mpi_package}
  %else
BuildRequires:  ptscotch-%{mpi_family}%{?mpi_ext}-devel
    %if 0%{?fedora}%{?rhel}
Requires:       ptscotch-%{mpi_family}%{?mpi_ext}
    %else
Requires:       libptscotch0-%{mpi_family}%{?mpi_ext}
    %endif
  %endif
%endif


# OpenFOAM compiles without debug, so skip all of these
%global debug_package %{nil}
%global _enable_debug_package 0
%global __os_install_post %{nil}
%define __debug_install_post %{nil}


%package common
Summary:        OpenFOAM common files
BuildArch:      noarch
Requires:       gawk
Requires:       m4
%if %{with foam_selector}
# Note: may cause issues on some builds - downgrade to Suggests?
Requires(post):  openfoam-selector
Requires(preun): openfoam-selector
%endif

%package devel
Summary:        OpenFOAM source code headers and wmake build chain
BuildArch:      noarch
Provides:       com.openfoam-devel = %{foam_api}
Requires:       %{name} = %{version}
Requires:       %{name}-tools = %{version}

%package tools
Summary:        OpenFOAM-specific build tools
Requires:       %{name}-common = %{version}
Requires:       gcc-c++
Requires:       make
Requires:       binutils

%package doc
Summary:        OpenFOAM documentation
BuildArch:      noarch
Provides:       com.openfoam-doc = %{foam_api}
Requires:       %{name}-common = %{version}

%package tutorials
Summary:        OpenFOAM tutorials
BuildArch:      noarch
Provides:       com.openfoam-tutorials = %{foam_api}
Requires:       %{name}-common = %{version}

%package default
Summary:        OpenFOAM default installation bundle
Provides:       com.openfoam-default = %{foam_api}
Requires:       %{name}-devel = %{version}
Requires:       %{name}-doc = %{version}
Requires:       %{name}-tutorials = %{version}

##Meta Packages##

%package -n openfoam
Summary:        Free, Open Source, Computational Fluid Dynamics Package
BuildArch:      noarch
Requires:       com.openfoam = %{foam_api}
Requires:       %{name}
%if %{with foam_selector}
# Note: may cause issues on some builds - downgrade to Suggests?
Requires(post):  openfoam-selector
Requires(preun): openfoam-selector
%endif

%package -n openfoam-devel
Summary:        OpenFOAM source code headers and wmake build chain
BuildArch:      noarch
Requires:       openfoam = %{version}
Requires:       com.openfoam-devel = %{foam_api}
Requires:       %{name}-devel

%package -n openfoam-default
Summary:        OpenFOAM default installation bundle
Requires:       openfoam-devel = %{version}
Requires:       com.openfoam-default = %{foam_api}
Requires:       %{name}-default


# Descriptions

%global _description1 %{expand:
OpenFOAM is a free, open source computational fluid dynamics (CFD)
software package produced by OpenCFD Ltd with twice yearly releases.}

%global _description2 %{expand:
* Release notes:  https://www.openfoam.com/news/main-news/openfoam-v%{foam_api}
* Documentation:  https://www.openfoam.com/documentation/
* Issue Tracker:  https://develop.openfoam.com/Development/openfoam/issues/}


%description            %_description1

It has a large user base across many areas of engineering and science,
used in academic, government and commercial organizations.

OpenFOAM has an extensive range of features to solve anything from
complex fluid flows involving chemical reactions, turbulence and heat
transfer, to solid dynamics and electromagnetics.
%_description2

Shell session:  %{shell_session}
Resource file:  %{prefix}/%{projectDir}/etc/bashrc

NOTE: The version in this package may not include any additional ParaView
reader plugins, runTimePostProcessing etc.


%description common     %_description1
%_description2

OpenFOAM common files.


%description devel      %_description1
%_description2

OpenFOAM source code headers and wmake build chain.


%description tools      %_description1
%_description2

Binaries for OpenFOAM-specific build tools.


%description doc        %_description1
%_description2

OpenFOAM documentation (manpages and doxygen templates).


%description tutorials  %_description1
%_description2

OpenFOAM tutorial examples.


%description default  %_description1
%_description2

OpenFOAM default installation bundle (binary, doc, develop, tutorial).

##Meta Packages##

%description -n openfoam  %_description1
%_description2

Meta-package for %{name}


%description -n openfoam-devel  %_description1
%_description2

Meta-package for %{name}-devel


%description -n openfoam-default  %_description1
%_description2

Meta-package for %{name}-default


#----
%prep
%setup -q -n %{projectTarDir}

# Eliminate version control remnants
find ./ -depth -name '.git*' -exec %{__rm} -rf '{}' ';'

# Use c++14 or newer for the newest CGAL, but not for rh7 (gcc = 4.8.5)
%if !0%{?el7}
wmake_rule="wmake/rules/General/Gcc/c++"
if [ -f "$wmake_rule" ]
then
    %{__sed} -i.orig -e 's/-std=c++11/-std=c++14/' "$wmake_rule"
fi
%endif

# Verify that expected installers are available
# - stop immediately if they are missing?
for installer in "%{dirInstaller}" "%{binInstaller}"
do
    if [ ! -x "$installer" ]
    then
        echo "Missing installer: $installer"
    fi
done


# Configure components
bin/tools/foamConfigurePaths \
    -version %{foam_api} \
    -boost boost-system \
    -cgal  %{?with_cgal:cgal-system}%{!?with_cgal:cgal-none} \
    -fftw  fftw-system \
    -kahip kahip-none \
    -metis metis-system \
    -scotch scotch-system \
    -paraview system \
    ;

# Directories for special generated output
for i in man1 scripts ThirdParty
do
    %{__mkdir_p} "build/package-tmp/$i"
done
echo "Third-party packages" >| build/package-tmp/ThirdParty/README

# Generate additional manpage
if [ -f doc/openfoam.1.in ]
then
    %{__sed} -e 's#OpenFOAM-[^\"]*#OpenFOAM-'"%{foam_api}#" \
        doc/openfoam.1.in | \
        %{__gzip} -c > build/package-tmp/man1/openfoam%{foam_api}.1.gz
fi


#-----
%build

%if 0%{?suse_version}
%define mpi_prefix %{_libdir}/mpi/gcc/openmpi%{?mpi_ext}
source %{mpi_prefix}/bin/mpivars.sh
FOAM_SYSTEM_MPI_LIBBIN="%{mpi_prefix}/lib64/openfoam%{foam_api}"
%endif

%if 0%{?fedora}%{?rhel}
%{_openmpi_load}
FOAM_SYSTEM_MPI_LIBBIN="${MPI_LIB}/openfoam%{foam_api}"
%endif

# Configure path to system openmpi (avoid mpicc runtime dependency)
if [ -x bin/tools/create-mpi-config ]
then
    bin/tools/create-mpi-config -write-openmpi
fi

# Stash build information (eg, for install stage)
echo "# Build configuration" >| build/package-tmp/build-config.sh
echo "export FOAM_SYSTEM_MPI_LIBBIN='${FOAM_SYSTEM_MPI_LIBBIN}'" \
    >> build/package-tmp/build-config.sh


# Avoid external influence on the environment
export FOAM_CONFIG_MODE="o"
unset FOAM_SETTINGS

# Before 2020-04 equivalent for FOAM_CONFIG_MODE
export FOAM_CONFIG_NOUSER=true

# When sourcing the bashrc file, some internal functions intentionally return
# non-zero which triggers the '-o errexit' in some bash versions

set +e  # Turn errexit off
source %{_builddir}/%{projectTarDir}/etc/bashrc '' || \
    echo "Ignore spurious sourcing error"

# Transitional: cleanup any old or dead links
for link in wmake/platforms platforms/tools
do
    readlink "$link" >/dev/null 2>&1 && %{__rm} -f "$link"
done
set -e  # Turn errexit back on

# Avoid external influence on the environment
unset FOAM_USER_APPBIN FOAM_USER_LIBBIN

# More stashed build information
echo "export FOAM_MPI='$FOAM_MPI'" >> build/package-tmp/build-config.sh
echo "export WM_MPLIB='$WM_MPLIB'" >> build/package-tmp/build-config.sh
echo "export WM_OPTIONS='$WM_OPTIONS'" >> build/package-tmp/build-config.sh
echo "# end" >> build/package-tmp/build-config.sh

if [ -x bin/tools/query-detect ]
then
    # Report some locations (useful for build error diagnosis)
    bin/tools/query-detect adios2 boost cgal fftw scotch
fi

./Allwmake -j -s -log=log.build

# Optional check of log file (detect build failures)
if :
then
    [ -f log.build ] || {
        echo "No log.build file - build failed entirely"
        exit 1
    }

    # Extract values from this type of content:
    #   api   = 1812
    #   patch = 190828
    #   bin   = 283 entries
    #   lib   = 139 entries

    bins="$( %{__cat} log.build | %{__sed} -ne 's/.*bin *= *\([0-9][0-9]*\).*/\1/p;' | %{__sed} -ne '$p' )"
    libs="$( %{__cat} log.build | %{__sed} -ne 's/.*lib *= *\([0-9][0-9]*\).*/\1/p;' | %{__sed} -ne '$p' )"

    if [ "${bins:=0}" = 0 ] || [ "${libs:=0}" = 0 ]
    then
        echo
        echo "Build failed with $bins executables and $libs libraries"
        echo "Check the log.build file"
        echo
        exit 1
    fi
    ## If we want to keep the build log
    # %{__gzip} -f9 log.build
fi

# ------------
# Transitional
# before 2020-04-03: wmake/platforms/linux64Gcc
# after  2020-04-03: platforms/tools/linux64Gcc

if [ -d platforms/tools ] && ! [ -e wmake/platforms ]
then
    # Provide old location as link
    (cd wmake && %{__ln_s} -f ../platforms/tools platforms)
elif [ -d wmake/platforms ] && ! [ -e platforms/tools ]
then
    # Provide new location as link
    (cd platforms && %{__ln_s} -f ../wmake/platforms tools)
fi

# ------------

# Generate manpages from executables
if [ -x bin/tools/foamCreateManpage ]
then
    bin/tools/foamCreateManpage \
        -gzip -output=build/package-tmp/man1 \
        -version="v%{foam_api}" || \
    echo "ignore problems generating manpages"
fi


#-------
%install
sourceDir="%{_builddir}/%{projectTarDir}"
targetDir="%{buildroot}%{prefix}/%{projectDir}"
packageTmp="${sourceDir}/build/package-tmp"
%{__mkdir_p} "$targetDir"

################
%{__cat} << README_PACKAGES > "$targetDir"/README.packages
User Group     What to install    Runtime  Compilation  Tutorials
minimalist      base package        yes         no          no
traditional     -devel              yes        yes          no
everything      -default            yes        yes         yes
README_PACKAGES
################

# ThirdParty (placeholder file or directory)
%{__cp} -a "$packageTmp"/ThirdParty "$targetDir"

# Modules directories (placeholder)
%{__mkdir_p} "$targetDir/modules"

installer="$sourceDir/%{dirInstaller}"
if [ -x "$installer" ]
then
    # common, devel, doc, tutorials. Collate module doc/tutorials
    "$installer" -v \
        -source="$sourceDir" \
        -prefix="$targetDir" \
        -all -collate

else
    # common, devel, doc, tutorials
    %{__cp} -a \
        "$sourceDir"/META-INFO \
        "$sourceDir"/applications \
        "$sourceDir"/bin \
        "$sourceDir"/doc \
        "$sourceDir"/etc \
        "$sourceDir"/src \
        "$sourceDir"/tutorials \
        "$sourceDir"/wmake \
        "$targetDir"

fi

# Various loose files
%{__cp} -a \
    "$sourceDir"/COPYING \
    "$sourceDir"/Allwmake \
    "$sourceDir"/README.md \
    "$targetDir"

# doc (man)
%{__cp} -a \
    "$packageTmp"/man1 \
    "$targetDir"/doc


# Retrieve stashed build-config information
# (FOAM_MPI, WM_OPTIONS, WM_MPLIB, ...)
. "$packageTmp/build-config.sh" ''

installer="$sourceDir/%{binInstaller}"
if [ -x "$installer" ]
then
    # bin,lib (no mpi)
    "$installer" -v \
        -source="$sourceDir" -platform="$WM_OPTIONS" \
        -prefix="$targetDir" \
        -no-mpi

    # lib (mpi-specific)
    %if 0%{?fedora} || (0%{?rhel} && !0%{?el7})
    # With rpm-mpi-hooks, must copy mpi-related into system MPI_LIB
    %{_openmpi_load}
    "$installer" -v \
        -source="$sourceDir" -platform="$WM_OPTIONS" -foam-mpi="$FOAM_MPI" \
        -mpi-libdir="%{buildroot}${FOAM_SYSTEM_MPI_LIBBIN}" \
        -mpi-only
    %{_openmpi_unload}
    %else
    # Install into normal OpenFOAM lib/ mpi directory
    "$installer" -v \
        -source="$sourceDir" -platform="$WM_OPTIONS" -foam-mpi="$FOAM_MPI" \
        -prefix="$targetDir" \
        -mpi-only
    %endif

    # tools
    %{__cp} -a \
        "$sourceDir"/platforms/tools \
        "$targetDir"/platforms

else
    # Platform-specific bin,lib (and tools)
    %{__cp} -a \
        "$sourceDir"/platforms \
        "$targetDir"
fi


# Create/install the update links trigger
triggerName="update-links-%{mpi_family}%{?mpi_ext}.sh"
trigger="$targetDir/platforms/$WM_OPTIONS/$triggerName"
updateLinks="$sourceDir/bin/tools/update-mpi-links.in"
if [ -f "$updateLinks" ]
then
    echo "Create $trigger"
    %{__sed} \
        -e "s#@FOAM_MPI@#${FOAM_MPI}#" \
        -e "s#@FOAM_SYSTEM_MPI_LIBBIN@#${FOAM_SYSTEM_MPI_LIBBIN}#" \
        "$updateLinks" >| "$trigger"
else
    echo '#!/bin/sh' >| "$trigger"
    echo 'echo "No trigger defined for %{mpi_family}%{?mpi_ext}"' >> "$trigger"
fi
%{__chmod} 0755 "$trigger"

# Link for 'openfoam' meta package
(cd %{buildroot}%{prefix} && %{__ln_s} openfoam%{foam_api} openfoam)


#----
%post
projectDir="${RPM_INSTALL_PREFIX}/%{projectDir}"
triggerName="update-links-%{mpi_family}%{?mpi_ext}.sh"

# Update mpi links (if any)
for trigger in "$projectDir"/platforms/*/"$triggerName"
do
    if [ -f "$trigger" ] && [ -x "$trigger" ]
    then
        "$trigger"
    fi
done


%post common
projectDir="${RPM_INSTALL_PREFIX}/%{projectDir}"

# Update installation directory
if [ -d "$projectDir" ]
then
(
    cd "$projectDir" && bin/tools/foamConfigurePaths \
        -project-path "${projectDir}"
)
fi

# Install shell-session script
session="%{shell_session}"
wrapper="$projectDir/bin/tools/openfoam.in"
if [ -f "$wrapper" ]
then
    echo "Create $session"
    %{__sed} -e "s#@PROJECT_DIR@#${projectDir}#" "$wrapper" >| "$session"
    %{__chmod} 0755 "$session"
else
    echo "No method to create $session for %{name}"
fi

# Register with openfoam-selector if possible
selector="%{_bindir}/openfoam-selector"
registerName="openfoam%{foam_api}"
if [ -x "$selector" ]
then
    if "$selector" \
        --register "${registerName}" \
        --source-dir "${projectDir}" \
        --yes
    then
        echo "Registered <${registerName}> with openfoam-selector"
    else
        echo "Failed to register <${registerName}> with openfoam-selector"
    fi
else
    echo "No openfoam-selector: skip registration of <${registerName}>"
fi


%post -n openfoam
projectDir="${RPM_INSTALL_PREFIX}/openfoam%{foam_api}"

# Create/update /usr/bin/openfoam -> openfoam{API} link
(
    cd %{_bindir} || exit

    if [ -f "openfoam%{foam_api}" ]
    then
        %{__ln_s} -f "openfoam%{foam_api}" openfoam
        echo "Create %{_bindir}/openfoam link for openfoam%{foam_api}"
    else
        echo "No plausible means to create %{_bindir}/openfoam link"
        %{__rm} -f %{_bindir}/openfoam
    fi
)

# Register with openfoam-selector if possible
selector="%{_bindir}/openfoam-selector"
registerName="openfoam"
if [ -x "$selector" ]
then
    if "$selector" \
        --register "${registerName}" \
        --source-dir "${projectDir}" \
        --yes
    then
        echo "Registered <${registerName}> with openfoam-selector"
    else
        echo "Failed to register <${registerName}> with openfoam-selector"
    fi
fi


#-----
%preun common
session="%{shell_session}"
selector="%{_bindir}/openfoam-selector"
registerName="openfoam%{foam_api}"

# Only unregister when uninstalling
if [ "$1" = "0" ]
then
    if [ -f "$session" ]
    then
        echo "Remove $session"
        %{__rm} -f -- "$session"
    fi

    # Deregister default if we are uninstalling it
    if [ -x "$selector" ]
    then
        if [ "$($selector --system --query)" = "${registerName}" ]
        then
            "$selector" --system --unset --yes
        fi
        if "$selector" --unregister "${registerName}" --yes
        then
            echo "Unregistered <${registerName}> from openfoam-selector"
        else
            echo "No <${registerName}> found to unregister from openfoam-selector"
        fi
    fi
fi

%preun -n openfoam
session="%{_bindir}/openfoam"
selector="%{_bindir}/openfoam-selector"
registerName="openfoam"

# Only unregister when uninstalling
if [ "$1" = "0" ]
then
    if linked=$(readlink "$session")
    then
        echo "Remove $session link for $linked"
    fi
    %{__rm} -f "$session"

    # Deregister default if we are uninstalling it
    if [ -x "$selector" ]
    then
        if [ "$($selector --system --query)" = "${registerName}" ]
        then
            "$selector" --system --unset --yes
        fi
        if "$selector" --unregister "${registerName}" --yes
        then
            echo "Unregistered <${registerName}> from openfoam-selector"
        else
            echo "No <${registerName}> found to unregister from openfoam-selector"
        fi
    fi
fi


#-----
%files
%if 0%{?fedora} || (0%{?rhel} && !0%{?el7})
# MPI libraries installed at system level (rpm-mpi-hooks)
%{_libdir}/openmpi/lib/openfoam%{foam_api}
%endif
%exclude %{prefix}/%{projectDir}/platforms/tools
%{prefix}/%{projectDir}/platforms


%files common
%doc %{prefix}/%{projectDir}/README.packages
# Include ownership of /usr/lib/openfoam prefix
%dir %{prefix}
%dir %{prefix}/%{projectDir}
%dir %{prefix}/%{projectDir}/modules
%dir %{prefix}/%{projectDir}/platforms
%dir %{prefix}/%{projectDir}/ThirdParty
%{prefix}/%{projectDir}/META-INFO
%{prefix}/%{projectDir}/bin
%{prefix}/%{projectDir}/etc
%{prefix}/%{projectDir}/COPYING
%{prefix}/%{projectDir}/README.md
%{prefix}/%{projectDir}/ThirdParty/README


%files devel
%exclude %{prefix}/%{projectDir}/wmake/platforms
%exclude %{prefix}/%{projectDir}/applications/test
%{prefix}/%{projectDir}/Allwmake
%{prefix}/%{projectDir}/applications
%{prefix}/%{projectDir}/src
%{prefix}/%{projectDir}/wmake


%files tools
%{prefix}/%{projectDir}/platforms/tools
%{prefix}/%{projectDir}/wmake/platforms


%files doc
%{prefix}/%{projectDir}/doc


%files tutorials
%{prefix}/%{projectDir}/tutorials


%files default
# No files


##Meta Packages##

%files -n openfoam
# Ownership of /usr/lib/openfoam/openfoam link
%{prefix}/openfoam


%files -n openfoam-devel
# No files


%files -n openfoam-default
# No files


#---------
%changelog
