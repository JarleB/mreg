from mreg.models import Host, Ipaddress, Network, PtrOverride

from .tests import clean_and_save, MregAPITestCase


class NetworksTestCase(MregAPITestCase):
    """"This class defines the test suite for api/networks """
    def setUp(self):
        """Define the test client and other variables."""
        super().setUp()
        self.network_sample = Network(network='10.0.0.0/24',
                                      description='some description',
                                      vlan=123,
                                      dns_delegated=False,
                                      category='so',
                                      location='Location 1',
                                      frozen=False)
        self.network_ipv6_sample = Network(network='2001:db8::/56',
                                           description='some IPv6 description',
                                           vlan=123,
                                           dns_delegated=False,
                                           category='so',
                                           location='Location 1',
                                           frozen=False)
        # Second samples are needed for the overlap tests
        self.network_sample_two = Network(network='10.0.1.0/28',
                                          description='some description',
                                          vlan=135,
                                          dns_delegated=False,
                                          category='so',
                                          location='Location 2',
                                          frozen=False)

        self.network_ipv6_sample_two = Network(network='2001:db8:0:1::/64',
                                               description='some IPv6 description',
                                               vlan=135,
                                               dns_delegated=False,
                                               category='so',
                                               location='Location 2',
                                               frozen=False)

        self.host_one = Host.objects.create(name='host1.example.org')
        clean_and_save(self.network_sample)
        clean_and_save(self.network_ipv6_sample)
        clean_and_save(self.network_sample_two)
        clean_and_save(self.network_ipv6_sample_two)

        self.patch_data = {
            'description': 'Test network',
            'vlan': '435',
            'dns_delegated': 'False',
            'category': 'si',
            'location': 'new-location'
        }
        self.patch_ipv6_data = {
            'description': 'Test IPv6 network',
            'vlan': '435',
            'dns_delegated': 'False',
            'category': 'si',
            'location': 'new-location'
        }

        self.patch_data_vlan = {'vlan': '435'}
        self.patch_data_network = {'network': '10.0.0.0/28'}
        self.patch_ipv6_data_network = {'network': '2001:db8::/64'}
        self.patch_data_network_overlap = {'network': '10.0.1.0/29'}
        self.patch_ipv6_data_network_overlap = {'network': '2001:db8:0:1::/64'}

        self.post_data = {
            'network': '192.0.2.0/29',
            'description': 'Test network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_ipv6_data = {
            'network': 'beef:feed::/32',
            'description': 'Test IPv6 network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_data_bad_ip = {
            'network': '192.0.2.0.95/29',
            'description': 'Test network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_ipv6_data_bad_ip = {
            'network': 'beef:good::/32',
            'description': 'Test IPv6 network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_data_bad_mask = {
            'network': '192.0.2.0/2549',
            'description': 'Test network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_ipv6_data_bad_mask = {
            'network': 'beef:feed::/129',
            'description': 'Test IPv6 network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_data_overlap = {
            'network': '10.0.1.0/29',
            'description': 'Test network',
            'vlan': '435',
            'dns_delegated': 'False',
        }
        self.post_ipv6_data_overlap = {
            'network': '2001:db8:0:1::/64',
            'description': 'Test IPv6 network',
            'vlan': '435',
            'dns_delegated': 'False',
        }

    def test_networks_post_201_created(self):
        """Posting a network should return 201"""
        ret = self.assert_post('/api/v1/networks/', self.post_data)
        self.assertEqual(ret['Location'], f'/api/v1/networks/{self.post_data["network"]}')

    def test_ipv6_networks_post_201_created(self):
        """Posting an IPv6 network should return 201"""
        self.assert_post('/networks/', self.post_ipv6_data)

    def test_networks_post_400_bad_request_ip(self):
        """Posting a network with a network that has a malformed IP should return 400"""
        self.assert_post_and_400('/networks/', self.post_data_bad_ip)

    def test_ipv6_networks_post_400_bad_request_ip(self):
        """Posting an IPv6 network with a network that has a malformed IP should return 400"""
        self.assert_post_and_400('/networks/', self.post_ipv6_data_bad_ip)

    def test_networks_post_400_bad_request_mask(self):
        """Posting a network with a network that has a malformed mask should return 400"""
        self.assert_post_and_400('/networks/', self.post_data_bad_mask)

    def test_ipv6_networks_post_400_bad_request_mask(self):
        """Posting an IPv6 network with a network that has a malformed mask should return 400"""
        self.assert_post_and_400('/networks/', self.post_ipv6_data_bad_mask)

    def test_networks_post_409_overlap_conflict(self):
        """Posting a network with a network which overlaps existing should return 409"""
        self.assert_post_and_409('/networks/', self.post_data_overlap)

    def test_ipv6_networks_post_409_overlap_conflict(self):
        """Posting an IPv6 network with a network which overlaps existing should return 409"""
        self.assert_post_and_409('/networks/', self.post_ipv6_data_overlap)

    def test_networks_get_200_ok(self):
        """GET on an existing ip-network should return 200 OK."""
        self.assert_get('/networks/%s' % self.network_sample.network)

    def test_ipv6_networks_get_200_ok(self):
        """GET on an existing ipv6-network should return 200 OK."""
        self.assert_get('/networks/%s' % self.network_ipv6_sample.network)

    def test_networks_list_200_ok(self):
        """GET without name should return a list and 200 OK."""
        response = self.assert_get('/networks/')
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(len(response.data['results']), 4)

    def test_networks_patch_204_no_content(self):
        """Patching an existing and valid entry should return 204 and Location"""
        response = self.assert_patch('/networks/%s' % self.network_sample.network,
                                     self.patch_data)
        self.assertEqual(response['Location'], '/api/v1/networks/%s' % self.network_sample.network)

    def test_ipv6_networks_patch_204_no_content(self):
        """Patching an existing and valid IPv6 entry should return 204 and Location"""
        response = self.assert_patch('/networks/%s' % self.network_ipv6_sample.network,
                                     self.patch_ipv6_data)
        self.assertEqual(response['Location'], '/api/v1/networks/%s' % self.network_ipv6_sample.network)

    def test_networks_patch_204_non_overlapping_network(self):
        """Patching an entry with a non-overlapping network should return 204"""
        response = self.assert_patch('/networks/%s' % self.network_sample.network,
                                     self.patch_data_network)
        self.assertEqual(response['Location'], '/api/v1/networks/%s' % self.patch_data_network['network'])

    def test_ipv6_networks_patch_204_non_overlapping_network(self):
        """Patching an entry with a non-overlapping IPv6 network should return 204"""
        response = self.assert_patch('/networks/%s' % self.network_ipv6_sample.network,
                                     self.patch_ipv6_data_network)
        self.assertEqual(response['Location'], '/api/v1/networks/%s' % self.patch_ipv6_data_network['network'])

    def test_networks_patch_400_bad_request(self):
        """Patching with invalid data should return 400"""
        self.assert_patch_and_400('/networks/%s' % self.network_sample.network,
                                  {'this': 'is', 'so': 'wrong'})

    def test_ipv6_networks_patch_400_bad_request(self):
        """Patching with invalid IPv6 data should return 400"""
        self.assert_patch_and_400('/networks/%s' % self.network_ipv6_sample.network,
                                  {'this': 'is', 'so': 'wrong'})

    def test_networks_patch_404_not_found(self):
        """Patching a non-existing entry should return 404"""
        self.assert_patch_and_404('/networks/193.101.168.0/29', self.patch_data)

    def test_ipv6_networks_patch_404_not_found(self):
        """Patching a non-existing IPv6 entry should return 404"""
        self.assert_patch_and_404('/networks/3000:4000:5000:6000::/64', self.patch_ipv6_data)

    def test_networks_patch_409_forbidden_network(self):
        """Patching an entry with an overlapping network should return 409"""
        self.assert_patch_and_409('/networks/%s' % self.network_sample.network,
                                  self.patch_data_network_overlap)

    def test_ipv6_networks_patch_409_forbidden_network(self):
        """Patching an IPv6 entry with an overlapping network should return 409"""
        self.assert_patch_and_409('/networks/%s' % self.network_ipv6_sample.network,
                                  self.patch_ipv6_data_network_overlap)

    def test_networks_get_network_by_ip_200_ok(self):
        """GET on an ip in a known network should return 200 OK."""
        response = self.assert_get('/networks/ip/10.0.0.5')
        self.assertEqual(response.data['network'], str(self.network_sample.network))


    def test_networks_get_one_ip_network_200_ok(self):
        """GET on an ip in a known network should return 200 OK."""
        obj = Network.objects.create(network='10.2.0.0/32')
        response = self.assert_get('/networks/ip/10.2.0.0')
        self.assertEqual(response.data['network'], str(obj.network))

    def test_ipv6_networks_get_network_by_ip_200_ok(self):
        """GET on an IPv6 in a known network should return 200 OK."""
        response = self.assert_get('/networks/ip/2001:db8::12')
        self.assertEqual(response.data['network'], str(self.network_ipv6_sample.network))

    def test_networks_get_network_by_invalid_ip_400_bad_request(self):
        """GET on an IP in a invalid network should return 400 bad request."""
        self.assert_get_and_400('/networks/ip/10.0.0.0.1')

    def test_networks_get_network_unknown_by_ip_404_not_found(self):
        """GET on an IP in a unknown network should return 404 not found."""
        self.assert_get_and_404('/networks/ip/127.0.0.1')

    def test_ipv6_networks_get_network_unknown_by_ip_404_not_found(self):
        """GET on an IPv6 in a unknown network should return 404 not found."""
        self.assert_get_and_404('/networks/ip/7000:8000:9000:a000::feed')

    def test_networks_get_usedcount_200_ok(self):
        """GET on /networks/<ip/mask>/used_count return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/used_count' % self.network_sample.network)
        self.assertEqual(response.data, 1)

    def test_ipv6_networks_get_usedcount_200_ok(self):
        """GET on /networks/<ipv6/mask>/used_count return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/used_count' % self.network_ipv6_sample.network)
        self.assertEqual(response.data, 1)

    def test_networks_get_usedlist_200_ok(self):
        """GET on /networks/<ip/mask>/used_list should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/used_list' % self.network_sample.network)
        self.assertEqual(response.data, ['10.0.0.17'])

    def test_networks_get_host_list_200_ok(self):
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/used_host_list' % self.network_sample.network)
        self.assertEqual(response.json(), {'10.0.0.17': ['host1.example.org']})

    def test_ipv6_networks_get_usedlist_200_ok(self):
        """GET on /networks/<ipv6/mask>/used_list should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/used_list' % self.network_ipv6_sample.network)
        self.assertEqual(response.data, ['2001:db8::beef'])

    def test_ipv6_networks_get_host_list_200_ok(self):
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/used_host_list' % self.network_ipv6_sample.network)
        self.assertEqual(response.json(), {'2001:db8::beef': ['host1.example.org']})

    def test_networks_get_unusedcount_200_ok(self):
        """GET on /networks/<ip/mask>/unused_count should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/unused_count' % self.network_sample.network)
        self.assertEqual(response.data, 250)

    def test_ipv6_networks_get_unusedcount_200_ok(self):
        """GET on /networks/<ipv6/mask>/unused_count should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/unused_count' % self.network_ipv6_sample.network)
        # :1 and :2 and :3 are reserved
        self.assertEqual(response.data, 4722366482869645213691)

    def test_networks_get_unusedlist_200_ok(self):
        """GET on /networks/<ip/mask>/unused_list should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/unused_list' % self.network_sample.network)
        self.assertEqual(len(response.data), 250)

    def test_ipv6_networks_get_unusedlist_200_ok(self):
        """GET on /networks/<ipv6/mask>/unused_list should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/unused_list' % self.network_ipv6_sample.network)
        self.assertEqual(len(response.data), 3997)

    def test_networks_get_first_unused_200_ok(self):
        """GET on /networks/<ip/mask>/first_unused should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='10.0.0.17')
        response = self.assert_get('/networks/%s/first_unused' % self.network_sample.network)
        self.assertEqual(response.data, '10.0.0.4')

    def test_ipv6_networks_get_first_unused_200_ok(self):
        """GET on /networks/<ipv6/mask>/first_unused should return 200 ok and data."""
        Ipaddress.objects.create(host=self.host_one, ipaddress='2001:db8::beef')
        response = self.assert_get('/networks/%s/first_unused' % self.network_ipv6_sample.network)
        self.assertEqual(response.data, '2001:db8::4')

    def test_networks_get_first_unued_on_full_network_404_not_found(self):
        """GET first unused IP on a full network should return 404 not found."""
        data = {
            'network': '172.16.0.0/30',
            'description': 'Tiny network',
        }
        self.assert_post('/networks/', data)
        self.assert_get_and_404('/networks/%s/first_unused' % data['network'])

    def test_reserved_is_less_or_equal_than_num_addresses(self):
        def _assert(network, excepted, reserved=3):
            data = {
                'network': network,
                'description': 'Tiny network',
                'reserved': reserved,
            }
            self.assert_post('/networks/', data)
            obj = Network.objects.get(network=data['network'])
            self.assertEqual(obj.reserved, excepted)
            self.assertLessEqual(obj.reserved, obj.network.num_addresses)

        _assert('172.16.0.0/30', 4, 8)
        _assert('172.16.0.4/31', 1, 1)
        _assert('172.16.0.6/32', 1, 2)
        _assert('2001:db8:1::/126', 4, 8)
        _assert('2001:db8:1::4/127', 1, 1)
        _assert('2001:db8:1::6/128', 1, 2)

    def test_networks_get_ptroverride_list(self):
        """GET on /networks/<ip/mask>/ptroverride_list should return 200 ok and data."""
        def _get_ptr_list():
            ret = self.assert_get('/networks/%s/ptroverride_list' % self.network_sample.network)
            return ret.data
        self.assertEqual(_get_ptr_list(), [])
        PtrOverride.objects.create(host=self.host_one, ipaddress='10.0.0.10')
        self.assertEqual(_get_ptr_list(), ['10.0.0.10'])

    def test_ipv6_networks_get_ptroverride_list(self):
        """GET on /networks/<ipv6/mask>/ptroverride_list should return 200 ok and data."""
        def _get_ptr_list():
            ret = self.assert_get('/networks/%s/ptroverride_list' % self.network_ipv6_sample.network)
            return ret.data
        self.assertEqual(_get_ptr_list(), [])
        PtrOverride.objects.create(host=self.host_one, ipaddress='2001:db8::feed')
        self.assertEqual(_get_ptr_list(), ['2001:db8::feed'])

    def test_networks_get_ptroverride_host_list(self):
        """GET on /networks/<ip/mask>/ptroverride_host_list should return 200 ok and data."""
        def _get_ptr_list():
            ret = self.assert_get('/networks/%s/ptroverride_host_list' % self.network_sample.network)
            return ret.data
        self.assertEqual(_get_ptr_list(), {})
        # Add two PtrOverrides to make sure it is sorted by IP
        PtrOverride.objects.create(host=self.host_one, ipaddress='10.0.0.10')
        PtrOverride.objects.create(host=self.host_one, ipaddress='10.0.0.20')
        self.assertEqual(_get_ptr_list(),
                         {'10.0.0.10': 'host1.example.org', '10.0.0.20': 'host1.example.org'})

    def test_ipv6_networks_get_ptroverride_host_list(self):
        """GET on /networks/<ip/mask>/ptroverride_host_list should return 200 ok and data."""
        def _get_ptr_list():
            ret = self.assert_get('/networks/%s/ptroverride_host_list' % self.network_ipv6_sample.network)
            return ret.data
        self.assertEqual(_get_ptr_list(), {})
        # Add two PtrOverrides to make sure it is sorted by IP
        PtrOverride.objects.create(host=self.host_one, ipaddress='2001:db8::10')
        PtrOverride.objects.create(host=self.host_one, ipaddress='2001:db8::20')
        self.assertEqual(_get_ptr_list(),
                         {'2001:db8::10': 'host1.example.org', '2001:db8::20': 'host1.example.org'})

    def test_networks_get_reserved_list(self):
        """GET on /networks/<ip/mask>/reserverd_list should return 200 ok and data."""
        response = self.assert_get('/networks/%s/reserved_list' % self.network_sample.network)
        self.assertEqual(response.data, ['10.0.0.0', '10.0.0.1',
                         '10.0.0.2', '10.0.0.3', '10.0.0.255'])

    def test_ipv6_networks_get_reserved_list(self):
        """GET on /networks/<ipv6/mask>/reserverd_list should return 200 ok and data."""
        response = self.assert_get('/networks/%s/reserved_list' % self.network_ipv6_sample.network)
        self.assertEqual(response.data, ['2001:db8::', '2001:db8::1',
                         '2001:db8::2', '2001:db8::3'])

    def test_networks_delete_204_no_content(self):
        """Deleting an existing entry with no adresses in use should return 204"""
        self.assert_post('/networks/', self.post_data)
        self.assert_delete('/networks/%s' % self.post_data['network'])

    def test_ipv6_networks_delete_204_no_content(self):
        """Deleting an existing IPv6 entry with no adresses in use should return 204"""
        self.assert_post('/networks/', self.post_ipv6_data)
        self.assert_delete('/networks/%s' % self.post_ipv6_data['network'])

    def test_networks_delete_409_conflict(self):
        """Deleting an existing entry with  adresses in use should return 409"""
        self.assert_post('/networks/', self.post_data)
        Ipaddress.objects.create(host=self.host_one, ipaddress='192.0.2.1')
        self.assert_delete_and_409('/networks/%s' % self.post_data['network'])

    def test_ipv6_networks_delete_409_conflict(self):
        """Deleting an existing IPv6 entry with adresses in use should return 409"""
        self.assert_post('/networks/', self.post_ipv6_data)
        Ipaddress.objects.create(host=self.host_one, ipaddress='beef:feed::beef')
        self.assert_delete_and_409('/networks/%s' % self.post_ipv6_data['network'])

    def test_client_must_be_logged_in(self):
        self.assert_get('/networks/')
        self.client.logout()
        self.assert_get_and_401('/networks/')


class NetworkAdminPermissions(MregAPITestCase):
    """Tests for the extra rights that members of NETWORK_ADMIN_GROUP
       have on Networks."""

    def setUp(self):
        self.client = self.get_token_client(username='networkadmin', superuser=False)
        self.add_user_to_groups('NETWORK_ADMIN_GROUP')

    def test_can_only_patch_reserved(self):
        """
        Test that members of NETWORK_ADMIN_GROUP can patch the reserved field, and
        that field only.
        """
        Network.objects.create(network='10.0.0.0/24', description='test')
        path = '/api/v1/networks/10.0.0.0/24'
        self.assert_patch(path, {'reserved': 5})
        self.assert_patch_and_403(path, {'description': 'test2'})
        # Only allowed to do a patch with reserved. Not other fields at the same time.
        self.assert_patch_and_403(path, {'reserved': 2, 'description': 'test2'})
