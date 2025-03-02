#!/usr/bin/env python3
# Copyright (c) 2016-2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the dumpwallet RPC."""
import os

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)


def read_dump(file_name, addrs, script_addrs, hd_master_addr_old):
    """
    Read the given dump, count the addrs that match, count change and reserve.
    Also check that the old hd_master is inactive
    """
    with open(file_name, encoding='utf8') as inputfile:
        found_legacy_addr = 0
        found_p2sh_segwit_addr = 0
        found_bech32_addr = 0
        found_script_addr = 0
        found_addr_chg = 0
        found_addr_rsv = 0
        witness_addr_ret = None
        hd_master_addr_ret = None
        for line in inputfile:
            # only read non comment lines
            if line[0] != "#" and len(line) > 10:
                # split out some data
                key_date_label, comment = line.split("#")
                key_date_label = key_date_label.split(" ")
                # key = key_date_label[0]
                date = key_date_label[1]
                keytype = key_date_label[2]

                imported_key = date == '1970-01-01T00:00:01Z'
                if imported_key:
                    # Imported keys have multiple addresses, no label (keypath) and timestamp
                    # Skip them
                    continue

                addr_keypath = comment.split(" addr=")[1]
                addr = addr_keypath.split(" ")[0]
                keypath = None
                if keytype == "inactivehdseed=1":
                    # ensure the old master is still available
                    assert (hd_master_addr_old == addr)
                elif keytype == "hdseed=1":
                    # ensure we have generated a new hd master key
                    assert (hd_master_addr_old != addr)
                    hd_master_addr_ret = addr
                elif keytype == "script=1":
                    # scripts don't have keypaths
                    keypath = None
                else:
                    keypath = addr_keypath.rstrip().split("hdkeypath=")[1]

<<<<<<< HEAD
                    # count key types
                    for addrObj in addrs:
                        if addrObj['address'] == addr.split(",")[0] and addrObj['hdkeypath'] == keypath and keytype == "label=":
                            # a labled entry in the wallet should contain both a native address
                            # and the p2sh-p2wpkh address that was added at wallet setup
                            if len(addr.split(",")) == 2:
                                addr_list = addr.split(",")
                                # the entry should be of the first key in the wallet
                                assert_equal(addrs[0]['address'], addr_list[0])
                                witness_addr_ret = addr_list[1]
                            found_addr += 1
                            break
                        elif keytype == "change=1":
                            found_addr_chg += 1
                            break
                        elif keytype == "reserve=1":
                            found_addr_rsv += 1
                            break
=======
                # count key types
                for addrObj in addrs:
                    if addrObj['address'] == addr.split(",")[0] and addrObj['hdkeypath'] == keypath and keytype == "label=":
                        if addr.startswith('m') or addr.startswith('n'):
                            # P2PKH address
                            found_legacy_addr += 1
                        elif addr.startswith('Q'):
                            # P2SH-segwit address
                            found_p2sh_segwit_addr += 1
                        elif addr.startswith('rgrlc1'):
                            found_bech32_addr += 1
                        break
                    elif keytype == "change=1":
                        found_addr_chg += 1
                        break
                    elif keytype == "reserve=1":
                        found_addr_rsv += 1
                        break
>>>>>>> 357020e93b90d687bb60cddd3c8bce954fad3764

                # count scripts
                for script_addr in script_addrs:
                    if script_addr == addr.rstrip() and keytype == "script=1":
                        found_script_addr += 1
                        break

<<<<<<< HEAD
        return found_addr, found_script_addr, found_addr_chg, found_addr_rsv, hd_master_addr_ret, witness_addr_ret
=======
        return found_legacy_addr, found_p2sh_segwit_addr, found_bech32_addr, found_script_addr, found_addr_chg, found_addr_rsv, hd_master_addr_ret
>>>>>>> 357020e93b90d687bb60cddd3c8bce954fad3764


class WalletDumpTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.extra_args = [["-keypool=90", "-addresstype=legacy"]]
        self.rpc_timeout = 120

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def setup_network(self):
        self.add_nodes(self.num_nodes, extra_args=self.extra_args)
        self.start_nodes()

    def run_test(self):
        wallet_unenc_dump = os.path.join(self.nodes[0].datadir, "wallet.unencrypted.dump")
        wallet_enc_dump = os.path.join(self.nodes[0].datadir, "wallet.encrypted.dump")

<<<<<<< HEAD
        # generate 20 addresses to compare against the dump
        # but since we add a p2sh-p2wpkh address for the first pubkey in the
        # wallet, we will expect 21 addresses in the dump
        test_addr_count = 20
=======
        # generate 30 addresses to compare against the dump
        # - 10 legacy P2PKH
        # - 10 P2SH-segwit
        # - 10 bech32
        test_addr_count = 10
>>>>>>> 357020e93b90d687bb60cddd3c8bce954fad3764
        addrs = []
        for address_type in ['legacy', 'p2sh-segwit', 'bech32']:
            for i in range(0, test_addr_count):
                addr = self.nodes[0].getnewaddress(address_type=address_type)
                vaddr = self.nodes[0].getaddressinfo(addr)  # required to get hd keypath
                addrs.append(vaddr)

        # Test scripts dump by adding a 1-of-1 multisig address
        multisig_addr = self.nodes[0].addmultisigaddress(1, [addrs[1]["address"]])["address"]

        # Refill the keypool. getnewaddress() refills the keypool *before* taking a key from
        # the keypool, so the final call to getnewaddress leaves the keypool with one key below
        # its capacity
        self.nodes[0].keypoolrefill()

        # dump unencrypted wallet
        result = self.nodes[0].dumpwallet(wallet_unenc_dump)
        assert_equal(result['filename'], wallet_unenc_dump)

<<<<<<< HEAD
        found_addr, found_script_addr, found_addr_chg, found_addr_rsv, hd_master_addr_unenc, witness_addr_ret = \
            read_dump(tmpdir + "/node0/wallet.unencrypted.dump", addrs, script_addrs, None)
        assert_equal(found_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_script_addr, 2)  # all scripts must be in the dump
        assert_equal(found_addr_chg, 50)  # 50 blocks where mined
        assert_equal(found_addr_rsv, 90*2) # 90 keys plus 100% internal keys
        assert_equal(witness_addr_ret, witness_addr) # p2sh-p2wsh address added to the first key
=======
        found_legacy_addr, found_p2sh_segwit_addr, found_bech32_addr, found_script_addr, found_addr_chg, found_addr_rsv, hd_master_addr_unenc = \
            read_dump(wallet_unenc_dump, addrs, [multisig_addr], None)
        assert_equal(found_legacy_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_p2sh_segwit_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_bech32_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_script_addr, 1)  # all scripts must be in the dump
        assert_equal(found_addr_chg, 0)  # 0 blocks where mined
        assert_equal(found_addr_rsv, 90 * 2)  # 90 keys plus 100% internal keys
>>>>>>> 357020e93b90d687bb60cddd3c8bce954fad3764

        # encrypt wallet, restart, unlock and dump
        self.nodes[0].encryptwallet('test')
        self.nodes[0].walletpassphrase('test', 10)
        # Should be a no-op:
        self.nodes[0].keypoolrefill()
        self.nodes[0].dumpwallet(wallet_enc_dump)

<<<<<<< HEAD
        found_addr, found_script_addr, found_addr_chg, found_addr_rsv, _, witness_addr_ret = \
            read_dump(tmpdir + "/node0/wallet.encrypted.dump", addrs, script_addrs, hd_master_addr_unenc)
        assert_equal(found_addr, test_addr_count)
        assert_equal(found_script_addr, 2)
        assert_equal(found_addr_chg, 90*2 + 50)  # old reserve keys are marked as change now
        assert_equal(found_addr_rsv, 90*2) 
        assert_equal(witness_addr_ret, witness_addr)
=======
        found_legacy_addr, found_p2sh_segwit_addr, found_bech32_addr, found_script_addr, found_addr_chg, found_addr_rsv, _ = \
            read_dump(wallet_enc_dump, addrs, [multisig_addr], hd_master_addr_unenc)
        assert_equal(found_legacy_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_p2sh_segwit_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_bech32_addr, test_addr_count)  # all keys must be in the dump
        assert_equal(found_script_addr, 1)
        assert_equal(found_addr_chg, 90 * 2)  # old reserve keys are marked as change now
        assert_equal(found_addr_rsv, 90 * 2)
>>>>>>> 357020e93b90d687bb60cddd3c8bce954fad3764

        # Overwriting should fail
        assert_raises_rpc_error(-8, "already exists", lambda: self.nodes[0].dumpwallet(wallet_enc_dump))

        # Restart node with new wallet, and test importwallet
        self.stop_node(0)
        self.start_node(0, ['-wallet=w2'])

        # Make sure the address is not IsMine before import
        result = self.nodes[0].getaddressinfo(multisig_addr)
        assert not result['ismine']

        self.nodes[0].importwallet(wallet_unenc_dump)

        # Now check IsMine is true
        result = self.nodes[0].getaddressinfo(multisig_addr)
        assert result['ismine']

if __name__ == '__main__':
    WalletDumpTest().main()
