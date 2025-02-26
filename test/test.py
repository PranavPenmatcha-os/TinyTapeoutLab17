#!/usr/bin/env python3
import os
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.result import TestFailure

@cocotb.test()
async def test_project(dut):
    """Test the bitwise operations functionality"""
    # Start the clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset values
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    # Release reset
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Testing bitwise operations")
    
    # First, test all edge cases to ensure basic functionality works
    test_cases = [
        # ui_in, uio_in, expected
        (0x00, 0x00, 0x00),  # All zeros
        (0xFF, 0x00, 0x7F),  # First input all ones, second all zeros, MSB is 1^0=1
        (0x00, 0xFF, 0x7F),  # First input all zeros, second all ones, MSB is 0^1=1
        (0xFF, 0xFF, 0x7F),  # Both inputs all ones, MSB is 1^1=0
        (0x80, 0x00, 0x80),  # Only ui_in MSB set
        (0x00, 0x80, 0x80),  # Only uio_in MSB set
        (0x80, 0x80, 0x00)   # Both MSBs set (should be 0 due to XOR)
    ]
    
    for idx, (ui_val, uio_val, expected) in enumerate(test_cases):
        dut.ui_in.value = ui_val
        dut.uio_in.value = uio_val
        
        await Timer(2, units="ns")  # Wait for combinational logic to settle
        
        actual = dut.uo_out.value
        
        # Comparing each bit for better debugging
        bin_actual = format(int(actual), '08b')
        bin_expected = format(expected, '08b')
        
        dut._log.info(f"Test {idx}: ui_in=0x{ui_val:02x} ({format(ui_val, '08b')}), "
                     f"uio_in=0x{uio_val:02x} ({format(uio_val, '08b')})")
        dut._log.info(f"Expected: 0x{expected:02x} ({bin_expected}), Got: 0x{actual:02x} ({bin_actual})")
        
        for bit_idx in range(8):
            exp_bit = (expected >> bit_idx) & 1
            act_bit = (int(actual) >> bit_idx) & 1
            
            if exp_bit != act_bit:
                dut._log.error(f"Bit {bit_idx} mismatch: expected {exp_bit}, got {act_bit}")
        
        if actual != expected:
            raise TestFailure(f"Test case {idx} failed! ui_in=0x{ui_val:02x}, uio_in=0x{uio_val:02x}, "
                             f"Expected: 0x{expected:02x}, Got: 0x{actual:02x}")
        
        await ClockCycles(dut.clk, 1)
    
    # Test with random inputs for more thorough coverage
    for i in range(50):
        ui_val = random.randint(0, 255)
        uio_val = random.randint(0, 255)
        
        dut.ui_in.value = ui_val
        dut.uio_in.value = uio_val
        
        await Timer(2, units="ns")
        
        # Calculate expected output
        expected_lower = (ui_val & 0x7F) | (uio_val & 0x7F)  # Bitwise OR for bits 0-6
        expected_msb = ((ui_val >> 7) & 1) ^ ((uio_val >> 7) & 1)  # XOR for bit 7
        expected = expected_lower | (expected_msb << 7)
        
        actual = dut.uo_out.value
        
        dut._log.info(f"Random test {i}: ui_in=0x{ui_val:02x}, uio_in=0x{uio_val:02x}")
        dut._log.info(f"Expected: 0x{expected:02x}, Got: 0x{actual:02x}")
        
        if actual != expected:
            # Detailed bit-by-bit comparison for better debugging
            for bit_idx in range(8):
                exp_bit = (expected >> bit_idx) & 1
                act_bit = (int(actual) >> bit_idx) & 1
                
                if exp_bit != act_bit:
                    dut._log.error(f"Bit {bit_idx} mismatch: expected {exp_bit}, got {act_bit}")
                    
            raise TestFailure(f"Random test {i} failed! ui_in=0x{ui_val:02x}, uio_in=0x{uio_val:02x}, "
                             f"Expected: 0x{expected:02x}, Got: 0x{actual:02x}")
        
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("All tests passed!")
