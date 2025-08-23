///////////////////////////////////////
//
//   Module Name: draw_line
//   Date Created: 08/21/25
//
//   Description:
//       Takes in line parameters, then performs an algorithm to
//       write individual pixels to make the line.
//
//       Needs one integer divider and a couple adders
//
//   Changes:
//   who | date   |  Description:
//   -----------------------------------------------------------------------------------
//   wng | 082125 |  1. Made initial file based on logic from python evaluation
//   wng | 082325 |  1. Simplified ending logic and improved state machine (removed a state)
//       |        |  2. Line drawing will now be twice as fast with same output




module draw_line (
    input logic clk,
    input logic [7:0] start_x_pos, // 8 bits unsigned
    input logic [6:0] start_y_pos, // 7 bits unsigned
    input logic [7:0] x_length,    // 8 bit  unsigned
    input logic [7:0] y_length,    // 8 bit  signed
    input logic start_line,
    output logic wr_valid,
    output logic [7:0] write_x_pos,
    output logic [6:0] write_y_pos,
    output logic running
);


localparam integer VGA_WIDTH_C = 160;
localparam integer VGA_HEIGHT_C = 120;

typedef enum logic {
    IDLE,
    WRITE_PIXELS
    //CHECK_EXIT,
    //DO_ADD
} line_state_t;

line_state_t line_state_reg = IDLE;

// pipelining some calculations before sending into the state machine

////////////////////////////////////////////////////////////////////
// Need fixed point data representation for slope
logic [13:0] x_length_fp; // Converting to S8.6, with 8 bits from port
assign x_length_fp = {7'b0000000, x_length};

logic [13:0] y_length_pos_fp, y_length_neg_fp, y_length_fp; // Converting to S8.6
assign y_length_pos_fp = {y_length, 6'b000000};   // y_length * 2^5
assign y_length_neg_fp = {~y_length+1, 6'b000000};
assign y_length_fp = (y_length[7] == 1) ? y_length_neg_fp : y_length_pos_fp;


logic [13:0] div_slope_pipe0;
logic zero_check_pipe0;

// S8.6
logic [13:0] slope_out_pipe1;

logic [7:0] x_max_pipe0, x_max_pipe1;
logic [7:0] y_max_pipe0, y_max_pipe1;

logic [6:0] vert_slope_pipe0; // get value for slope if it is a vertical line

// pipeline delay other signals
logic [7:0] y_length_pipe0;
logic       y_sign_pipe0,      y_sign_pipe1;
logic [7:0] start_x_pos_pipe0, start_x_pos_pipe1;
logic [6:0] start_y_pos_pipe0, start_y_pos_pipe1;
logic       start_line_pipe0,  start_line_pipe1;

always_ff @(posedge clk) begin
    // First pipeline stage
    // To get a real fixed-point representation:
    // shift the divisor left by number of fractional bits
    // SLOPE IS S8.6
    div_slope_pipe0 <= y_length_fp / x_length_fp;
    // = 2^5 * (y_length/x_length)
    // if treating as S8.6 => dividing by 2^5, so give proper result

    zero_check_pipe0 <= (y_length == 0) ? 1 : 0;

    x_max_pipe0    <= start_x_pos + x_length;
    y_max_pipe0 <= {1'b0, start_y_pos} + y_length;

    y_length_pipe0 <= y_length;

    // if (y_length[7] == 0) begin
    //     y_max_pipe0      <= start_y_pos + y_length[6:0];
    //     vert_slope_pipe0 <= y_length[6:0];
    // end else begin
    //     y_max_pipe0      <= (y_length[6:0] > start_y_pos) ? 0 : start_y_pos - y_length[6:0];
    // end

    // Delay
    start_x_pos_pipe0 <= start_x_pos;
    start_y_pos_pipe0 <= start_y_pos;

    y_sign_pipe0   <= y_length[7];


    //x_length_pipe0 <= x_length; DON'T NEED ANYMORE
    //y_length_pipe0 <= y_length[6:0]; // length is 7, with one sign bit
    start_line_pipe0 <= start_line;


    ///////////////////////////////////
    // Second pipeline stage

    // if the denominator was zero, then it is a vertical line (so make slope max)
    // INSTEAD OF THIS, SET TO THE Y_LENGTH
    slope_out_pipe1 <= (zero_check_pipe0) ? y_length_pipe0 : ((y_sign_pipe0) ? ~div_slope_pipe0 + 1 : div_slope_pipe0);

    // Delay
    start_x_pos_pipe1 <= start_x_pos_pipe0;
    start_y_pos_pipe1 <= start_y_pos_pipe0;

    x_max_pipe1 <= (x_max_pipe0 > VGA_WIDTH_C) ? VGA_WIDTH_C : x_max_pipe0;
    
    // THIS IGNORES THE CASE OF OVERFLOW, CONSIDER HOW TO HANDLE THAT
    if (y_max_pipe0[7] == 1) begin
        y_max_pipe1 <= 0;//(y_max_pipe0 > VGA_WIDTH_C) ? VGA_WIDTH_C : y_max_pipe0;
    end else begin
        y_max_pipe1 <= (y_max_pipe0 > VGA_WIDTH_C) ? VGA_WIDTH_C : y_max_pipe0;
    end

    //x_length_pipe1 <= x_length_pipe0;
    //y_length_pipe1 <= y_length_pipe0;

    y_sign_pipe1   <= y_sign_pipe0;

    start_line_pipe1 <= start_line_pipe0;

end

////////////////////////////////////////////////////////////////////

// State machine
// "{name}_n" is the next state value
// "{name}_reg" is the actual register

// holds the ideal value of the line, using fixed-point notation
logic [13:0] y_ideal_reg;
logic [13:0] slope_reg;

// holds the real added value 
logic [6:0] y_added_reg; // only need 6 bits here because we can only go the height
logic [7:0] x_added_reg;


//logic [6:0] y_length_reg;
//logic [7:0] x_length_reg;
logic [7:0] x_max_reg;
logic [6:0] y_max_reg;

logic [13:0] y_difference;

// increment logic
logic inc_y_reg, inc_x_reg, inc_ideal_reg;


logic x_diff_reg;

logic [7:0] x_pos_out_reg;
logic [6:0] y_pos_out_reg;
logic [6:0] y_add_value_reg;

logic wr_valid_reg;

// next state logic
always_ff @(posedge clk) begin

    line_state_reg <= line_state_reg;
    y_ideal_reg <= y_ideal_reg;
    slope_reg <= slope_reg;
    y_added_reg <= y_added_reg;
    x_added_reg <= x_added_reg;
    x_diff_reg  <= x_diff_reg;
    //x_length_reg <= x_length_reg;
    //y_length_reg <= y_length_reg;
    x_max_reg <= x_max_reg;
    y_max_reg <= y_max_reg;

    // make 0 unless we explicitly set to non-zero
    wr_valid_reg <= 0;
    

    case (line_state_reg)
        IDLE: begin
            y_ideal_reg <= {1'b0, start_y_pos_pipe1, 6'b0};
            slope_reg <= slope_out_pipe1;
            y_added_reg <= 0;

            x_added_reg <= 0;
            x_diff_reg  <= 0;

            // initialize values
            x_pos_out_reg  <= start_x_pos_pipe1;
            y_pos_out_reg  <= start_y_pos_pipe1;

            // copy values from pipeline
            x_max_reg <= x_max_pipe1;
            y_max_reg <= y_max_pipe1;

            y_add_value_reg <= (y_sign_pipe1) ? 7'h7f : 7'h1;

            if (start_line_pipe1) begin
                line_state_reg <= WRITE_PIXELS;
                wr_valid_reg   <= 1; // make sure the initial value is written
            end

        end

        WRITE_PIXELS : begin

            wr_valid_reg <= 1;

            if (x_pos_out_reg == x_max_reg && y_pos_out_reg == y_max_reg) begin
            
                line_state_reg <= IDLE;
            
            end else begin
                if (y_pos_out_reg == y_ideal_reg[12:6]) begin

                    y_pos_out_reg <= y_pos_out_reg + y_add_value_reg;
                
                end else begin
                
                    if (x_pos_out_reg != x_max_reg) begin
                        x_pos_out_reg <= x_pos_out_reg + 1;
                    end
                    if (y_pos_out_reg != y_max_reg) begin
                        y_ideal_reg <= y_ideal_reg + slope_reg;
                    end
                
                end

            end
        end

        // // This state is needed to allow for the increment logic to be performed and registered
        // CHECK_EXIT : begin
        //     if (x_added_reg >= x_length_reg && y_added_reg >= y_length_reg) begin
        //         line_state_reg <= IDLE;
        //     end else begin
        //         line_state_reg <= DO_ADD;
        //     end
        // end

        // DO_ADD : begin
        //     // write this cycle
        //     line_state_reg <= CHECK_EXIT;

        //     if (inc_y_reg) begin
        //         wr_valid_reg <= 1;
        //         y_added_reg <= y_added_reg + 1;
        //         y_pos_out_reg <= y_pos_out_reg + y_add_value_reg;
        //     end

        //     if (inc_x_reg) begin
        //         wr_valid_reg <= 1;
        //         x_diff_reg <= 0;
        //         x_added_reg <= x_added_reg + 1;
        //         x_pos_out_reg <= x_pos_out_reg + 1;
        //     end

        //     if (inc_ideal_reg) begin
        //         x_diff_reg <= 1;
        //         y_ideal_reg <= y_ideal_reg + slope_reg;
        //     end
        // end

        default : begin
            line_state_reg <= IDLE;
        end
    endcase


end


//////////////////////////////////////////////////////////////////////////
// combinationally get difference to pass through rest of inc logic
// y ideal is 14 bits (U8.5)
// y added is 7  bits (U7)
//      => need to add one MSb, 5 LSb to match size
// assign y_difference = y_ideal_reg - {1'b0, y_added_reg, 5'b00000};

// // increment logic for line drawing
// always_ff @(posedge clk) begin
//     if (y_difference[12] == 0) begin
//         inc_y_reg = 1;
//         inc_x_reg = 0;
//         inc_ideal_reg = 0;
//     end else if (x_diff_reg) begin
//         inc_y_reg = 0;
//         inc_x_reg = 1;
//         inc_ideal_reg = 0;
//     end else begin
//         inc_y_reg = 0;
//         inc_x_reg = 0;
//         inc_ideal_reg = 1;
//     end
// end


// Assign output values
assign wr_valid = wr_valid_reg;
assign write_x_pos = x_pos_out_reg;
assign write_y_pos = y_pos_out_reg;
assign running = (line_state_reg == WRITE_PIXELS);


endmodule