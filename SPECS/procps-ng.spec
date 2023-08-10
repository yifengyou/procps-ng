# The testsuite is unsuitable for running on buildsystems
%global tests_enabled 0

Summary: System and process monitoring utilities
Name: procps-ng
Version: 3.3.15
Release: 13%{?dist}
License: GPL+ and GPLv2 and GPLv2+ and GPLv3+ and LGPLv2+
Group: Applications/System
URL: https://sourceforge.net/projects/procps-ng/

Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.xz
# README files are missing in latest tarball
# wget https://gitlab.com/procps-ng/procps/raw/e0784ddaed30d095bb1d9a8ad6b5a23d10a212c4/README.md
Source1: README.md
# wget https://gitlab.com/procps-ng/procps/raw/e0784ddaed30d095bb1d9a8ad6b5a23d10a212c4/top/README.top
Source2: README.top

Patch1: procps-ng-3.3.15-pidof-show-worker-threads.patch
Patch2: procps-ng-3.3.15-pgrep-uid-conversion-overflow.patch
Patch3: procps-ng-3.3.15-vmstat-watch-manpage.patch
Patch4: procps-ng-3.3.15-pidof-kernel-workers-option.patch
Patch5: procps-ng-3.3.15-pidof-separator-option-backport.patch
Patch6: procps-ng-3.3.15-uptime-pretty-mod.patch
Patch7: procps-ng-3.3.15-vmstat-omit-first-report.patch
Patch8: procps-ng-3.3.15-sysctl-config-dir-order.patch
Patch9: procps-ng-3.3.15-pgrep-uid-gid-overflow.patch
Patch10: procps-ng-3.3.15-display-sig-unsafe.patch
Patch11: procps-ng-3.3.15-ps-select.patch
Patch12: procps-ng-3.3.15-ps-out-of-bonds-read.patch

BuildRequires: ncurses-devel
BuildRequires: libtool
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gcc
BuildRequires: gettext-devel
BuildRequires: systemd-devel
BuildRequires: git

%if %{tests_enabled}
BuildRequires: dejagnu
%endif

Provides: procps = %{version}-%{release}
Obsoletes: procps < 3.2.9-1

# usrmove hack - will be removed once initscripts are fixed
Provides: /sbin/sysctl
Provides: /bin/ps


%description
The procps package contains a set of system utilities that provide
system information. Procps includes ps, free, skill, pkill, pgrep,
snice, tload, top, uptime, vmstat, pidof, pmap, slabtop, w, watch
and pwdx.
The ps command displays a snapshot of running processes. The top command
provides a repetitive update of the statuses of running processes.
The free command displays the amounts of free and used memory on your
system. The skill command sends a terminate command (or another
specified signal) to a specified set of processes. The snice
command is used to change the scheduling priority of specified
processes. The tload command prints a graph of the current system
load average to a specified tty. The uptime command displays the
current time, how long the system has been running, how many users
are logged on, and system load averages for the past one, five,
and fifteen minutes. The w command displays a list of the users
who are currently logged on and what they are running. The watch
program watches a running program. The vmstat command displays
virtual memory statistics about processes, memory, paging, block
I/O, traps, and CPU activity. The pwdx command reports the current
working directory of a process or processes.

%package devel
Summary:  System and process monitoring utilities
Group:    Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Provides: procps-devel = %{version}-%{release}
Obsoletes: procps-devel < 3.2.9-1

%description devel
System and process monitoring utilities development headers

%package i18n
Summary:  Internationalization pack for procps-ng
Group:    Applications/System
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

# fortunately the same release number for f21 and f22
Conflicts: man-pages-de < 1.7-3
Conflicts: man-pages-fr < 3.66-3
Conflicts: man-pages-pl < 0.7-5

%description i18n
Internationalization pack for procps-ng

%prep
%autosetup -S git
cp -p %{SOURCE1} .
cp -p %{SOURCE2} top/


%build
# The following stuff is needed for git archives only
#echo "%{version}" > .tarball-version
#./autogen.sh

autoreconf --verbose --force --install

%configure \
           --exec-prefix=/ \
           --docdir=/unwanted \
           --disable-static \
           --enable-w-from \
           --disable-kill \
           --enable-watch8bit \
           --enable-skill \
           --enable-sigwinch \
           --enable-libselinux \
           --with-systemd \
           --disable-modern-top

make CFLAGS="%{optflags}"


%if %{tests_enabled}
%check
make check
%endif


%install
make DESTDIR=%{buildroot} install

# translated man pages
find man-po/ -type d -maxdepth 1 -mindepth 1 | while read dirname; do cp -a $dirname %{buildroot}%{_mandir}/ ; done
rm -f %{buildroot}%{_mandir}/{de,fr,uk}/man1/kill.1

%find_lang %{name} --all-name --with-man

ln -s %{_bindir}/pidof %{buildroot}%{_sbindir}/pidof

%ldconfig_scriptlets

%files
%doc AUTHORS Documentation/bugs.md Documentation/FAQ NEWS README.md top/README.top Documentation/TODO
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LIB
%{_libdir}/libprocps.so.*
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_mandir}/man5/*


%exclude %{_libdir}/libprocps.la
%exclude /unwanted/*

%files devel
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LIB
%{_libdir}/libprocps.so
%{_libdir}/pkgconfig/libprocps.pc
%{_includedir}/proc
%{_mandir}/man3/*

%files i18n -f %{name}.lang

%changelog
* Tue Jan 17 2023 Jan Rybar <jrybar@redhat.com> - 3.3.15-13
- version bump requested to create -devel subpkg for CRB inclusion
- Resolves: rhbz#2164781

* Tue Jan 17 2023 Jan Rybar <jrybar@redhat.com> - 3.3.15-12
- ps: out-of-bonds read in quick mode
- Resolves: rhbz#2153813

* Tue Dec 13 2022 Kyle Walker <kwalker@redhat.com> - 3.3.15-11
- ps: revert increase command name length to 64 ____ (catch up)
- Resolves: rhbz#2144978

* Wed Nov 23 2022 Jan Rybar <jrybar@redhat.com> - 3.3.15-10
- display.c: backport: async-signal-unsafe handler deadlocks on SIGHUP
- Resolves: rhbz#2141696

* Wed Aug 17 2022 Jan Rybar <jrybar@redhat.com> - 3.3.15-9
- pgrep: backport uid/gid overflow fix
- Resolves: rhbz#1827731

* Wed Jul 20 2022 Jan Rybar <jrybar@redhat.com> - 3.3.15-8
- vmstat: added -y option to omit first report
- Resolves: rhbz#2027350
- sysctl: backport config directory order, align with systemd
- Resolves: rhbz#2111915

* Wed Mar 23 2022 Jan Rybar <jrybar@redhat.com> - 3.3.15-7
- uptime: human readable data not shown if 364 days up
- Resolves: rhbz#1772999

* Tue Dec 01 2020 Jan Rybar <jrybar@redhat.com> - 3.3.15-6
- pidof: option for separator collides with other option
- Resolves: rhbz#1895985

* Mon Nov 09 2020 Jan Rybar <jrybar@redhat.com> - 3.3.15-5
- version bump due to unspotted malformed backport patch
- Resolves: rhbz#1860486
- Resolves: rhbz#1894526
- Related: rhbz#1803640

* Fri Nov 06 2020 Jan Rybar <jrybar@redhat.com> - 3.3.15-4
- pidof: new option to show kernel worker threads
- pidof: empty input causes to show kernel worker threads
- Resolves: rhbz#1860486
- Resolves: rhbz#1894526
- Related: rhbz#1803640
- 
* Wed Jul 08 2020 Jan Rybar <jrybar@redhat.com> - 3.3.15-3
- pgrep: uid/gid conversion overflow
- vmstat: align manpage with procfs wording
- watch: manpage presumes NTP on system
- Resolves: rhbz#1827731
- Resolves: rhbz#1829920
- Resolves: rhbz#1583669

* Tue Apr 14 2020 Jan Rybar <jrybar@redhat.com> - 3.3.15-2
- pidof: show kernel workers
- gating activated
- Resolves: rhbz#1803640

* Wed Jul 04 2018 Jan Rybar <jrybar@redhat.com> - 3.3.15-1
- Rebase to 3.3.15
- Translated manual pages moved to -i18n subpackage

* Wed Feb 21 2018 Michael Cronenworth <mike@cchtml.com> - 3.3.12-1
- Upgrading to 3.3.12

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.3.10-18
- Escape macros in %%changelog

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.10-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.3.10-16
- Switch to %%ldconfig_scriptlets

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.10-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.10-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.10-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 28 2016 Lubomir Rintel - 3.3.10-12
- Fix FTBFS with new systemd

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.10-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jaromir Capik <jcapik@redhat.com> - 3.3.10-10
- Enhancing find_elf_note to allow calling lib functions with dlopen (#1287752)

* Fri Aug 14 2015 Adam Jackson <ajax@redhat.com> 3.3.10-9
- Use %%configure so the hardened cflags get applied correctly

* Mon Aug 10 2015 Jaromir Capik <jcapik@redhat.com> - 3.3.10-8
- Fixing crashes in 'top' when a deep forking appears (#1153642)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.10-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 3.3.10-6
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Tue Nov 25 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.10-5
- Fixing locale dirs ownership (#1167443)

* Mon Oct 20 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.10-4
- Bringing the old 'top' defaults back (#1153049)

* Mon Oct 06 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.10-3
- Resolving file conflicts with man-pages-*
- Replacing hardcoded paths with macros
- Making the i18n subpackage noarch

* Tue Sep 30 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.10-2
- Removing explicit dependency on systemd-libs
- Removing /etc/sysctl.d (ownership quietly stolen by systemd)

* Tue Sep 09 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.10-1
- Upgrading to 3.3.10

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.9-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 Tom Callaway <spot@fedoraproject.org> - 3.3.9-11
- fix license handling

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.9-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 30 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-9
- Dropping Cached -= Shmem (#963799)

* Tue Apr 08 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-8
- Documenting the 't' process state code in the ps manual (#946864)

* Fri Mar 14 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-7
- Fixing sysctl line length limit (#1071530)

* Thu Feb 27 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-6
- Subtracting Shmem from Cached (#1070736)

* Wed Feb 05 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-5
- Support for timestamps & wide diskstat (#1053428, #1025833)
- Fixing fd leak in watch
- Fixing format-security build issues

* Fri Jan 24 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-4
- Skipping trailing zeros in read_unvectored (#1057600)

* Mon Jan 20 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-3
- 'vmstat -w' was not wide enough (#1025833)

* Tue Jan 07 2014 Jaromir Capik <jcapik@redhat.com> - 3.3.9-2
- Replacing the /sbin/pidof wrapper with symlink

* Tue Dec 03 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.9-1
- Update to 3.3.9

* Mon Nov 04 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-17
- Fixing pidof compilation warnings
- RPM workaround - changing sysvinit-tools Conflicts/Obsoletes (#1026504)

* Wed Oct 16 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-16
- Introducing pidof (#987064)

* Tue Sep 17 2013 Aristeu Rozanski <aris@redhat.com> - 3.3.8-15
- Introduce namespaces support (#1016242)

* Tue Sep 17 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-14
- top: Fixing missing newline when running in the batch mode (#1008674)

* Fri Aug 09 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-13
- Including forgotten man fixes (#948522)

* Wed Aug 07 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-12
- Fixing the license tag

* Wed Aug 07 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-11
- Support for libselinux (#975459)
- Support for systemd (#994457)
- Support for 'Shmem' in free (#993271)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jul 19 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-9
- RH man page scan (#948522)

* Tue Jul 02 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-8
- Extending the end-of-job patch disabling the screen content restoration

* Mon Jul 01 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-7
- Disabling screen content restoration when exiting 'top' (#977561)
- Enabling SIGWINCH flood prevention

* Wed Jun 26 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-6
- Avoiding "write error" messages when piping to grep (#976199)

* Wed Jun 26 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-5
- Disabling tests - unsuitable for running on buildsystems

* Mon Jun 17 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-4
- Enabling skill and snice (#974752)

* Wed Jun 12 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-3
- Adding major version in the libnuma soname

* Thu May 30 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-2
- watch: enabling UTF-8 (#965867)

* Wed May 29 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.8-1
- Update to 3.3.8

* Wed May 22 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.7-4
- top: inoculated against a window manager like 'screen' (#962022)

* Tue Apr 16 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.7-3
- Avoid segfaults when reading zero bytes - file2str (#951391)

* Mon Apr 15 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.7-2
- Moving libprocps.pc to the devel subpackage (#951726)

* Tue Mar 26 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.7-1
- Update to 3.3.7
- Reverting upstream commit for testsuite/unix.exp

* Tue Feb 05 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.6-4
- Fixing empty pmap output on ppc/s390 (#906457)

* Tue Jan 15 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.6-3
- Typo in the description, pdwx instead of pwdx (#891476)

* Tue Jan 08 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.6-2
- Rebuilding with tests disabled (koji issue #853084)

* Tue Jan 08 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.6-1
- Update to 3.3.6
- Changing URL/Source from gitorious to recently created sourceforge page
- Replacing autogen.sh with autoreconf

* Mon Jan 07 2013 Jaromir Capik <jcapik@redhat.com> - 3.3.5-1
- Update to 3.3.5

* Tue Dec 11 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.4-2
- fixing the following regressions:
-   negative ETIME field in ps (#871819)
-   procps states a bug is hit when receiving a signal (#871824)
-   allow core file generation by ps command (#871825)

* Tue Dec 11 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.4-1
- Update to 3.3.4

* Tue Sep 25 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.3-3.20120807git
- SELinux spelling fixes (#859900)

* Tue Aug 21 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.3-2.20120807git
- Tests enabled

* Tue Aug 07 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.3-1.20120807git
- Update to 3.3.3-20120807git

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar 08 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.2-3
- Second usrmove hack - providing /bin/ps

* Tue Mar 06 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.2-2
- Fixing requires in the devel subpackage (missing %%{?_isa} macro)
- License statement clarification (upstream patch referrenced in the spec header)

* Mon Feb 27 2012 Jaromir Capik <jcapik@redhat.com> - 3.3.2-1
- Initial version
