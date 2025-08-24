`timescale 1ns / 1ps

///////////////////////////////////////
//
//   Module Name: draw_line_tb
//   Date Created: 08/21/25
//
//   Description:
//       Tests draw_line module
//
//   Changes:
//   who | date   |  Description:
//   -----------------------------------------------------------------------------------
//   wng | 082125 |  1. Made initial file based on logic from python evaluation
//   wng | 082325 |  1. Added task to automatically draw lines


module draw_line_tb ();



// Display SRAM representation
logic sram [120][160] = {default: 0};

logic clk_tb;

logic [7:0] start_x_tb;
logic [6:0] start_y_tb;
logic [7:0] x_length_tb;
logic [7:0] y_length_tb;
logic start_line_tb = 0;
logic wr_valid_tb;
logic [7:0] write_x_pos_tb;
logic [6:0] write_y_pos_tb;
logic running_tb;


draw_line inst_uut (
    .clk(clk_tb),
    .start_x_pos(start_x_tb),
    .start_y_pos(start_y_tb),
    .x_length(x_length_tb),
    .y_length(y_length_tb),
    .start_line(start_line_tb),
    .wr_valid(wr_valid_tb),
    .write_x_pos(write_x_pos_tb),
    .write_y_pos(write_y_pos_tb),
    .running(running_tb)
);


localparam clk_period = 1ns;

always begin
    clk_tb = 1;
    #(clk_period);
    clk_tb = 0;
    #(clk_period);
end

always_ff @(posedge clk_tb) begin

    if (wr_valid_tb) begin
        if (write_x_pos_tb < 160 && write_y_pos_tb < 120) begin
            sram[write_x_pos_tb][write_y_pos_tb] = 1;
        end
    end

end


task start_line_draw (
    input logic [7:0] start_x,
    input logic [6:0] start_y,
    input logic [7:0] x_len,
    input logic [7:0] y_len
);
    @(posedge clk_tb);
    start_x_tb <= start_x;
    start_y_tb <= start_y;
    x_length_tb <= x_len;
    y_length_tb <= y_len;
    start_line_tb <= 1;
    @(posedge clk_tb);
    start_line_tb <= 0;
    @(negedge running_tb);
    @(posedge clk_tb);

endtask


initial begin

    // start_x_tb <= 28;
    // start_y_tb <= 7;
    // x_length_tb <= 20;
    // y_length_tb <= 17;
    // @(posedge clk_tb);
    // start_line_tb <= 1;
    // @(posedge clk_tb);
    // start_line_tb <= 0;
    // @(posedge clk_tb);
    // @(negedge running_tb);

    // @(posedge clk_tb);
    // start_x_tb <= 12;
    // start_y_tb <= 15;
    // x_length_tb <= 10;
    // y_length_tb <= -4;
    // start_line_tb <= 1;
    // @(posedge clk_tb);
    // start_line_tb <= 0;
    // @(negedge running_tb);

    // @(posedge clk_tb);
    // start_x_tb <= 50;
    // start_y_tb <= 0;
    // x_length_tb <= 10;
    // y_length_tb <= 0;
    // start_line_tb <= 1;
    start_line_draw(50, 0, 10, 0);
    start_line_draw(0, 40, 0, 10);
    start_line_draw(59, 49, 0, -10);
    start_line_draw(0, 0, 60, 50);
    start_line_draw(0, 49, 60, -50);
    start_line_draw(0,0,0,-5);
    start_line_draw(150, 110, 20, 20);


    for (int y_ind = 0; y_ind < 50; y_ind++) begin
        for (int x_ind = 0; x_ind < 60; x_ind++) begin
            if (sram[x_ind][y_ind] == 1) begin
                $write("1 ");
            end else begin
                $write("0 ");
            end
        end
        $write("\n");
    end

    $finish;
end


endmodule




