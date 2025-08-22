


module draw_line (
    input logic clk,
    input logic [7:0] start_x_pos, // 8 bits unsigned
    input logic [6:0] start_y_pos, // 7 bits unsigned
    input logic [7:0] x_length,    // 8 bit unsigned
    input logic [7:0] y_length,    // 8 bit signed-magnitude
    input logic start_line,
    output logic wr_valid,
    output logic [7:0] write_x_pos,
    output logic [6:0] write_y_pos,
    output logic running
);


typedef enum logic [1:0] {
    IDLE,
    CHECK_EXIT,
    DO_ADD
} line_state_t;

line_state_t line_state_reg = IDLE;

// pipelining some calculations before sending into the state machine

////////////////////////////////////////////////////////////////////
// Need fixed point data representation for slope
logic [12:0] x_length_fp; // Converting to U8.5, with 8 bits from port
assign x_length_fp = {5'b00000, x_length};

logic [12:0] y_length_fp; // Converting to U8.5
assign y_length_fp = {1'b0, y_length[6:0], 5'b00000};

logic [12:0] div_slope;
logic zero_check;

logic [12:0] slope_out;

// pipeline delay other signals
logic [7:0] x_length_dly0,    x_length_dly1;
logic [6:0] y_length_dly0,    y_length_dly1;
logic       y_sign_dly0,      y_sign_dly1;
logic [7:0] start_x_pos_dly0, start_x_pos_dly1;
logic [6:0] start_y_pos_dly0, start_y_pos_dly1;
logic       start_line_dly0,  start_line_dly1;

always_ff @(posedge clk) begin
    // First pipeline stage
    // To get a real fixed-point representation:
    // shift the divisor left by number of fractional bits
    div_slope <= y_length_fp / x_length_fp;
    zero_check <= (y_length == 0) ? 1 : 0;

    // Delay
    start_x_pos_dly0 <= start_x_pos;
    start_y_pos_dly0 <= start_y_pos;

    x_length_dly0 <= x_length;
    y_length_dly0 <= y_length[6:0]; // length is 7, with one sign bit
    y_sign_dly0   <= y_length[7];

    start_line_dly0 <= start_line;


    ///////////////////////////////////
    // Second pipeline stage

    // if the denominator was zero, then it is a vertical line (so make slope max)
    slope_out <= (zero_check) ? 13'h1fff : div_slope;

    // Delay
    start_x_pos_dly1 <= start_x_pos_dly0;
    start_y_pos_dly1 <= start_y_pos_dly0;

    x_length_dly1 <= x_length_dly0;
    y_length_dly1 <= y_length_dly0;
    y_sign_dly1   <= y_sign_dly0;

    start_line_dly1 <= start_line_dly0;

end

////////////////////////////////////////////////////////////////////

// State machine
// "{name}_n" is the next state value
// "{name}_reg" is the actual register

// holds the ideal value of the line, using fixed-point notation
logic [12:0] y_ideal_reg;
logic [12:0] slope_reg;

// holds the real added value 
logic [6:0] y_added_reg; // only need 6 bits here because we can only go the height
logic [7:0] x_added_reg;


logic [6:0] y_length_reg;
logic [7:0] x_length_reg;

logic [12:0] y_difference;

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
    x_length_reg <= x_length_reg;
    y_length_reg <= y_length_reg;

    // make 0 unless we explicitly set to non-zero
    wr_valid_reg <= 0;
    

    case (line_state_reg)
        IDLE: begin
            y_ideal_reg <= 0;
            slope_reg <= slope_out;
            y_added_reg <= 0;

            x_added_reg <= 0;
            x_diff_reg  <= 0;

            if (start_line_dly1) begin
                line_state_reg <= CHECK_EXIT;
                wr_valid_reg   <= 1; // make sure the initial value is written
                
                y_add_value_reg <= (y_sign_dly1) ? 7'h7f : 7'h1;

                // initialize values
                x_pos_out_reg  <= start_x_pos_dly1;
                y_pos_out_reg  <= start_y_pos_dly1;
                x_length_reg <= x_length_dly1;
                y_length_reg <= y_length_dly1;
            end

        end

        // This state is needed to allow for the increment logic to be performed and registered
        CHECK_EXIT : begin
            if (x_added_reg >= x_length_reg && y_added_reg >= y_length_reg) begin
                line_state_reg <= IDLE;
            end else begin
                line_state_reg <= DO_ADD;
            end
        end

        DO_ADD : begin
            // write this cycle
            line_state_reg <= CHECK_EXIT;

            if (inc_y_reg) begin
                wr_valid_reg <= 1;
                y_added_reg <= y_added_reg + 1;
                y_pos_out_reg <= y_pos_out_reg + y_add_value_reg;
            end

            if (inc_x_reg) begin
                wr_valid_reg <= 1;
                x_diff_reg <= 0;
                x_added_reg <= x_added_reg + 1;
                x_pos_out_reg <= x_pos_out_reg + 1;
            end

            if (inc_ideal_reg) begin
                x_diff_reg <= 1;
                y_ideal_reg <= y_ideal_reg + slope_reg;
            end
        end

        default : begin
            line_state_reg <= IDLE;
        end
    endcase


end


//////////////////////////////////////////////////////////////////////////
// combinationally get difference to pass through rest of inc logic
// y ideal is 13 bits (U8.5)
// y added is 7  bits (U7)
//      => need to add one MSb, 5 LSb to match size
assign y_difference = y_ideal_reg - {1'b0, y_added_reg, 5'b00000};

// increment logic for line drawing
always_ff @(posedge clk) begin
    if (y_difference[12] == 0) begin
        inc_y_reg = 1;
        inc_x_reg = 0;
        inc_ideal_reg = 0;
    end else if (x_diff_reg) begin
        inc_y_reg = 0;
        inc_x_reg = 1;
        inc_ideal_reg = 0;
    end else begin
        inc_y_reg = 0;
        inc_x_reg = 0;
        inc_ideal_reg = 1;
    end
end


// Assign output values
assign wr_valid = wr_valid_reg;
assign write_x_pos = x_pos_out_reg;
assign write_y_pos = y_pos_out_reg;
assign running = (line_state_reg == CHECK_EXIT) || (line_state_reg == DO_ADD);


endmodule