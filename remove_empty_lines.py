def remove_empty_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Remove empty lines and lines with only whitespace
    non_empty_lines = [line for line in lines if line.strip()]
    
    with open(output_file, 'w') as f:
        f.writelines(non_empty_lines)

if __name__ == "__main__":
    input_file = "input.txt"  # Change this to your input file path
    output_file = "output.txt"  # Change this to your desired output file path
    remove_empty_lines(input_file, output_file) 