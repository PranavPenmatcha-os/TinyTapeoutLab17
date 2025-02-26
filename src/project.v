/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none
module tt_um_bitwiseOperator (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    // Bitwise OR for bits 0-6
    assign uo_out[6:0] = ui_in[6:0] | uio_in[6:0]; // First 7 bits
    
    // For bit 7, it should be XOR of ui_in[7] and uio_in[7]
    assign uo_out[7] = ui_in[7] ^ uio_in[7];
    
    // Set unused outputs to 0
    assign uio_out = 8'h00;
    assign uio_oe = 8'h00;
    
    // Properly format the unused signals
    wire _unused_ok = &{1'b0, ena, clk, rst_n};
endmodule
