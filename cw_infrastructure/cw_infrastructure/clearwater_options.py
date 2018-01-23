#
# @file project_clearwater_options.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import os

import validators as vlds
import check_config_utilities as utils
from check_config_utilities import Option


def get_options():
    """Set up the list of options to be validated"""
    options = [
        Option('local_ip', Option.MANDATORY, vlds.ip_addr_validator),
        Option('public_ip', Option.MANDATORY, vlds.ip_addr_validator),
        Option('public_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.resolvable_domain_name_validator)),
        Option('home_domain', Option.MANDATORY, vlds.domain_name_validator),
        Option('sprout_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_validator)),
        Option('hs_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),

        Option('homestead_diameter_watchdog_timer', Option.OPTIONAL,
               vlds.create_integer_range_validator(min_value=6)),
        Option('ralf_diameter_watchdog_timer', Option.OPTIONAL,
               vlds.create_integer_range_validator(min_value=6)),

        # Mandatory nature of one of these is enforced below
        Option('etcd_cluster', Option.OPTIONAL, vlds.ip_addr_list_validator),
        Option('etcd_proxy', Option.OPTIONAL, vlds.ip_addr_list_validator),

        # Mandatory nature of one of these is enforced below
        Option('hss_realm', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.diameter_realm_validator)),
        Option('hss_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.domain_name_validator)),
        Option('hs_provisioning_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),

        Option('snmp_ip', Option.SUGGESTED, vlds.ip_addr_list_validator),
        Option('sas_server', Option.SUGGESTED, vlds.ip_or_domain_name_validator),

        Option('scscf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),
        Option('bgcf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),
        Option('icscf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),

        Option('enum_server', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.resolveable_ip_or_domain_name_list_validator)),
        Option('signaling_dns_server', Option.OPTIONAL, vlds.ip_addr_list_validator),
        Option('remote_cassandra_seeds', Option.OPTIONAL, vlds.ip_addr_validator),
        Option('billing_realm', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.diameter_realm_validator)),
        Option('node_idx', Option.OPTIONAL, vlds.integer_validator),
        Option('ralf_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),
        Option('xdms_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),

        Option('alias_list', Option.DEPRECATED),
        Option('always_serve_remote_aliases', Option.OPTIONAL, vlds.flag_validator)
    ]
    return options


def validate_hss_config():
    """
    Require that the site is either configured with a HSS, or HS Prov.
    """

    hss_config = utils.number_present('hss_realm',
                                      'hss_hostname')

    hs_prov_config = utils.number_present('hs_provisioning_hostname')

    if hss_config > 0 and hs_prov_config > 0:
        utils.error('HSS',
                    ('Both a HSS and Homestead Subscriber Store are configured. '
                     'Either a HSS should be configured (with hss_realm and/or '
                     'hss_hostname), or Homestead Subscriber Store should be '
                     'configured (with hs_provisioning_hostname set).'))
        return utils.ERROR
    elif hss_config == 0 and hs_prov_config == 0:
        utils.error('HSS',
                    ('Either a HSS must be configured (with hss_realm and/or'
                     '  hss_hostname), or Homestead Subscriber Store must be'
                     ' configured (with hs_provisioning_hostname set).'))
        return utils.ERROR

    return utils.OK


def validate_etcd_config():
    """Require that exactly one of etcd_proxy or etcd_cluster is set"""
    etcd_config = utils.number_present('etcd_proxy', 'etcd_cluster')

    if etcd_config > 1:
        utils.error('etcd',
                    'Only one of etcd_proxy and etcd_cluster may be set')
        return utils.ERROR

    elif etcd_config == 0:
        utils.error('etcd', 'One of etcd_proxy and etcd_cluster must be set')
        return utils.ERROR

    return utils.OK


def validate_sprout_hostname():
    """Check that the default URIs based on the Sprout hostname are valid"""

    sprout_hostname = os.environ.get('sprout_hostname')

    status = utils.OK

    for sproutlet in ('scscf', 'bgcf', 'icscf'):

        # If the default hasn't been overriden, check that the URI
        # based on the Sprout hostname is a valid SIP URI
        if not os.environ.get('{}_uri'.format(sproutlet)):
            uri = 'sip:{}.{};transport=TCP'.format(sproutlet, sprout_hostname)
            code = vlds.run_in_sig_ns(vlds.sip_uri_validator)('sprout_hostname',
                                                              uri)
            if code > status:
                status = code

    return status


def check_advanced_config():
    """
    More advanced checks (e.g. checking consistency between multiple options)
    can be performed here.
    """
    status = utils.OK

    code = validate_hss_config()

    if code > status:
        status = code

    code = validate_etcd_config()

    if code > status:
        status = code

    code = validate_sprout_hostname()

    if code > status:
        status = code

    return status
