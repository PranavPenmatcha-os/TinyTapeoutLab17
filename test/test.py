#!/usr/bin/env python3
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles
from cocotb.result import TestFailure

@cocotb.test()
async def test_project(dut):
    """Test bitwise operations with simple test cases"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Initialize and reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Define simple test cases
    test_cases = [
        # ui_in, uio_in, expected_output
        (0b00000000, 0b00000000, 0b00000000),  # All zeros
        (0b01010101, 0b10101010, 0b11111111),  # Alternating patterns, OR gives all 1s, XOR of MSBs is 1
        (0b10101010, 0b01010101, 0b11111111),  # Alternating patterns, OR gives all 1s, XOR of MSBs is 1
        (0b11111111, 0b11111111, 0b01111111),  # All ones, MSB is 1^1=0
        (0b10000000, 0b00000000, 0b10000000),  # Only MSB in ui_in
        (0b00000000, 0b10000000, 0b10000000),  # Only MSB in uio_in
        (0b10000000, 0b10000000, 0b00000000),  # MSB in both, XOR gives 0
        (0b01111111, 0b00000000, 0b01111111),  # All lower bits in ui_in
        (0b00000000, 0b01111111, 0b01111111),  # All lower bits in uio_in
        (0b01111111, 0b01111111, 0b01111111)   # All lower bits in both
    ]
    
    for i, (ui_val, uio_val, expected) in enumerate(test_cases):
        dut.ui_in.value = ui_val
        dut.uio_in.value = uio_val
        
        await Timer(2, units="ns")
        
        actual = int(dut.uo_out.value)
        
        dut._log.info(f"Test {i}: ui_in={format(ui_val, '08b')}, uio_in={format(uio_val, '08b')}")
        dut._log.info(f"Expected: {format(expected, '08b')}, Got: {format(actual, '08b')}")
        
        if actual != expected:
            for bit_idx in range(8):
                exp_bit = (expected >> bit_idx) & 1
                act_bit = (actual >> bit_idx) & 1
                
                if exp_bit != act_bit:
                    dut._log.error(f"Bit {bit_idx} mismatch: expected {exp_bit}, got {act_bit}")
                    
            raise TestFailure(f"Test case {i} failed! Expected: {format(expected, '08b')}, Got: {format(actual, '08b')}")
        
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("All tests passed!")
