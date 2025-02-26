#!/usr/bin/env python3
import os
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

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
    
    # Test a set of random values
    for _ in range(100):
        ui_val = random.randint(0, 255)
        uio_val = random.randint(0, 255)
        
        dut.ui_in.value = ui_val
        dut.uio_in.value = uio_val
        
        await Timer(2, units="ns")  # Wait for combinational logic to settle
        
        # Expected results calculation
        expected_lower_bits = (ui_val & 0x7F) | (uio_val & 0x7F)  # Bitwise OR of bits 0-6
        expected_msb = ((ui_val >> 7) & 1) ^ ((uio_val >> 7) & 1)  # XOR of MSBs
        expected = (expected_msb << 7) | expected_lower_bits
        
        actual = dut.uo_out.value
        
        assert actual == expected, f"Test failed! ui_in=0x{ui_val:02x}, uio_in=0x{uio_val:02x}, Expected: 0x{expected:02x}, Got: 0x{actual:02x}"
        
        await ClockCycles(dut.clk, 1)
    
    # Test specific edge cases
    test_cases = [
        {"ui_in": 0x00, "uio_in": 0x00, "expected": 0x00},  # All zeros
        {"ui_in": 0xFF, "uio_in": 0x00, "expected": 0x7F},  # First input all ones, second all zeros
        {"ui_in": 0x00, "uio_in": 0xFF, "expected": 0x7F},  # First input all zeros, second all ones
        {"ui_in": 0xFF, "uio_in": 0xFF, "expected": 0x7F},  # Both inputs all ones
        {"ui_in": 0x80, "uio_in": 0x80, "expected": 0x00},  # Both MSBs set, should be 0 due to XOR
        {"ui_in": 0x80, "uio_in": 0x00, "expected": 0x80},  # Only first MSB set
        {"ui_in": 0x00, "uio_in": 0x80, "expected": 0x80},  # Only second MSB set
        {"ui_in": 0x7F, "uio_in": 0x7F, "expected": 0x7F}   # All lower bits set
    ]
    
    for test in test_cases:
        dut.ui_in.value = test["ui_in"]
        dut.uio_in.value = test["uio_in"]
        
        await Timer(2, units="ns")
        
        actual = dut.uo_out.value
        expected = test["expected"]
        
        assert actual == expected, f"Edge case failed! ui_in=0x{test['ui_in']:02x}, uio_in=0x{test['uio_in']:02x}, Expected: 0x{expected:02x}, Got: 0x{actual:02x}"
        
        await ClockCycles(dut.clk, 1)
    
    print("All tests passed!")
