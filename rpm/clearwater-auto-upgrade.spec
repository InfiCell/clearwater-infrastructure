Name:           clearwater-auto-upgrade
Summary:        Package enabling automatic upgrade of Clearwater software
BuildArch:      noarch
BuildRequires:  python2-devel python-virtualenv
Requires:       redhat-lsb-core clearwater-infrastructure

%include %{rootdir}/build-infra/cw-rpm.spec.inc

%description
Package enabling automatic upgrade of Clearwater software

%install
. %{rootdir}/build-infra/cw-rpm-utils clearwater-auto-upgrade %{rootdir} %{buildroot}
setup_buildroot
copy_to_buildroot debian/clearwater-auto-upgrade.init.d /etc/init.d clearwater-auto-upgrade
build_files_list > clearwater-auto-upgrade.files

%post
/sbin/chkconfig clearwater-auto-upgrade on
/sbin/service clearwater-auto-upgrade restart

%preun
# Uninstall, not upgrade
if [ "$1" == 0 ] ; then
  /sbin/chkconfig clearwater-auto-upgrade off
fi

%files -f clearwater-auto-upgrade.files
