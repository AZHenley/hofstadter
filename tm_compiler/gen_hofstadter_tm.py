import sys, os

#---- dicts to be used later (should have done this from the begining)
states_dict = {}
alphabet_dict = {}
tape_val_dict = {}
line_count = 0
#---- Structs for the TM
class state():
    def __init__(self, state_name: str, is_start: bool, is_accept: bool):
        self.state_name = state_name
        self.is_start = is_start
        self.is_accept = is_accept
        self.transitions_from = []

class transition():
    def __init__(self, from_state: str, to_state: str, reading_str: str, writing_str: str, movement: str):
        self.from_state = from_state
        self.to_state = to_state
        self.reading_str = reading_str
        self.writing_str = writing_str
        self.movement = movement

#---- Make sure we have all of the arguments needed (tape_input) is not nessesary
# Just give it what it wants, I really don't want to do any error checcking
if len(sys.argv) < 3:
    print("python gen_hofstadter_tm.py [TM_File] [Tape_length] \"Tape_input\"")
    exit()
elif len(sys.argv) == 4 and int(sys.argv[2]) < len(sys.argv[3]):
    print("Tape_input is longer than Tape_length")
    exit()

folders = ["tm_values", "tape_ids", "tape_inputs", "states", "alphabet"]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)


#---- Get the arguments provided
hofstadter_tm = open("hofstadter_tm.txt", 'w')
my_tm = open(sys.argv[1], 'r')
tape_length = int(sys.argv[2])
tape_input = ""
if len(sys.argv) == 4:
    tape_input = sys.argv[3]
alphabet = []
for char in tape_input:
    if char not in alphabet and char != "~":
        alphabet.append(char)
print(sys.argv[3])

#---- Generate the hash line (used to terminate when tape is done printing) and other values
f = open("tm_values/hash_line.txt", 'w')
f.write("####################################")
f.close()
hofstadter_tm.write("tm_values/hash_line.txt\n")
line_count += 1
f = open("tm_values/running.txt", 'w')
f.write("running")
f.close()
f = open("tm_values/accept.txt", 'w')
f.write("accept")
f.close()
f = open("tm_values/reject.txt", 'w')
f.write("reject")
f.close()
f = open("tm_values/new_line.txt", 'w')
f.write("\n")
f.close()

#---- Gen state info
# Get the number of states
tm_line = my_tm.readline()
tm_line = my_tm.readline()
number_of_states = int(tm_line)
# Get each state
tm_line = my_tm.readline().strip()


end_of_tape_and_states = 1 + tape_length*2 + 1 + number_of_states


#---- Clears directorys
for f in os.listdir("tape_ids"):
    os.remove("tape_ids/"+f)
for f in os.listdir("tape_inputs"):
    os.remove("tape_inputs/"+f)
for f in os.listdir("states"):
    os.remove("states/"+f)
for f in os.listdir("alphabet"):
    os.remove("alphabet/"+f)
f = open("tm_out.txt", 'w')
f.close()
os.remove("tm_out.txt")

#---- Generate the needed files for defining input 
for i in range(tape_length):
    # Geneterate tape id files
    f = open("tape_ids/tape_"+str(i)+"_id.txt", 'w')
    f.write("t"+str(i))
    f.close()
    hofstadter_tm.write("tape_ids/tape_"+str(i)+"_id.txt\n")
    line_count += 1
    # Generate tape input files
    if i < len(tape_input):
        f = open("tape_inputs/tape_"+str(i)+".txt", 'w')
        f.write(tape_input[i])
        f.close()
        hofstadter_tm.write("tape_inputs/tape_"+str(i)+".txt\n")
        line_count += 1
        tape_val_dict[str(i)] = line_count
    else:
        if i == len(tape_input):
            f = open("tape_inputs/default.txt", 'w')
            f.write("_")
            f.close()
        hofstadter_tm.write("tape_inputs/default.txt\n")
        line_count += 1
        tape_val_dict[str(i)] = line_count

hofstadter_tm.write("tm_values/hash_line.txt\n")
line_count += 1
#---- Write the states to the file and generate files
states = []
while (tm_line := my_tm.readline().strip()) != "Transitions:":
    line_list = tm_line.split()
    temp_state = state("----"+line_list[0], "start" in line_list, "accept" in line_list)
    states.append(temp_state)
    f = open("states/"+temp_state.state_name+".txt", 'w')
    f.write(temp_state.state_name)
    f.close()
    hofstadter_tm.write("states/"+temp_state.state_name+".txt\n")
    line_count += 1
    states_dict[temp_state.state_name] = line_count

#---- Get all the transitions and build onto the alphabet
while True:
    tm_line = my_tm.readline().split()
    if not tm_line:
        break
    temp_transition = transition("----"+tm_line[0], "----"+tm_line[1], tm_line[2], tm_line[3], tm_line[4])
    state_element: state
    for i in range(len(states)):
        if states[i].state_name == temp_transition.from_state:
            states[i].transitions_from.append(temp_transition)
            if temp_transition.reading_str not in alphabet and temp_transition.reading_str != "~":
                alphabet.append(temp_transition.reading_str)
            if temp_transition.writing_str not in alphabet and temp_transition.writing_str != "~":
                alphabet.append(temp_transition.writing_str)



#---- Update all of the transitions (if there is a '~' wild card)

for i, s in enumerate(states):
    transition_characters = [x.reading_str for x in s.transitions_from]
    if '~' in transition_characters:
        # Get the transisition that has the ~
        wild_transition = s.transitions_from[transition_characters.index('~')]
        for other_char in [x for x in alphabet if x not in transition_characters]:
            temp_writing_char = wild_transition.writing_str
            if wild_transition.writing_str == '~':
                temp_writing_char = other_char
            temp_transition = transition(wild_transition.from_state, wild_transition.to_state, other_char, temp_writing_char, wild_transition.movement)
            s.transitions_from.append(temp_transition)
            

        s.transitions_from.remove(wild_transition)
    transition_characters = [x.reading_str for x in s.transitions_from]



#---- The folowing lines to be added to the hofstadter file represent the head of the TM amd if the machine is running or not
for i in range(len(states)):
    if states[i].is_start:
        hofstadter_tm.write("states/"+states[i].state_name+".txt\n") # Starting state and current state @ end_of_tape_and_states + 1
        line_count += 1
        break
hofstadter_tm.write("tape_ids/tape_0_id.txt\n") # Starting tape poisition @ end_of_tape_and_states + 2
line_count += 1
hofstadter_tm.write("+3\n") # starting tape value @ end_of_tape_and_states + 3 ###### <- We actually might not use this line
line_count += 1
hofstadter_tm.write("tm_values/running.txt\n") # is the machine running, rejected, or accepted? (initialize to running) @ end_of_tape_and_states + 4 
line_count += 1
# Here we will just store a few values that the machine can be in
hofstadter_tm.write("tm_values/accept.txt\n") # @ end_of_tape_and_states + 5
line_count += 1
hofstadter_tm.write("tm_values/reject.txt\n") # @ end_of_tape_and_states + 6
line_count += 1


#---- Include the printing the tape to console
machine_state_pos = end_of_tape_and_states + 4
print_info_start = machine_state_pos + 3 # the plus to is for the machine state  as well as the first hash
#hofstadter_tm.write("@0 +"+str(machine_state_pos)+" # !"+str(print_info_start)+'\n')
hofstadter_tm.write('\n')
line_count += 1
# hofstadter_tm.write("@0 +1 # !"+str(print_info_start+1)+"\n")
hofstadter_tm.write('\n')
line_count += 1
for i in range((tape_length)*2):
    # hofstadter_tm.write("@0 +"+str(i+2))
    if i%2:
        # hofstadter_tm.write(" # !"+str(i+print_info_start+2)+"\n")
        hofstadter_tm.write('\n')
        line_count += 1
    else:
        # hofstadter_tm.write(" ?"+str(end_of_tape_and_states+2)+" @0 +"+str(end_of_tape_and_states+1)+" # !"+str(i+print_info_start+2)+"\n")
        hofstadter_tm.write('\n')
        line_count += 1
# hofstadter_tm.write("@0 +"+str(tape_length*2 + 2)+" @"+str(print_info_start+2+2*tape_length)+" @"+str(print_info_start+2+2*tape_length)+" @"+str(print_info_start+2+2*tape_length)+" # @"+str(print_info_start+2+2*tape_length)+" !"+str(print_info_start+2+2*tape_length)+"\n")
hofstadter_tm.write('\n')
line_count += 1

#---- Create alphabet files and place into file
for i, char in enumerate(alphabet):
    f = open("alphabet/"+str(i)+'-'+char+".txt",'w')
    f.write(char)
    f.close()
    hofstadter_tm.write("alphabet/"+str(i)+'-'+char+".txt\n")
    line_count += 1
    alphabet_dict[char] = line_count


#---- Write all of the transitions to the file
total_number_transitions = number_of_states*tape_length*len(alphabet)
current_state = machine_state_pos - 3
current_tape_pos = machine_state_pos - 2
print("current tape pos", current_tape_pos)

current_tape_val = machine_state_pos - 1 # We might not need this
machine_state = machine_state_pos
accept_val = machine_state + 1
reject_val = machine_state + 2
first_state_name = tape_length*2 + 3
first_alphabet = reject_val + first_state_name + 1

#---- Implement the clock
line_count += 1
clock_pos = str(line_count)
hofstadter_tm.write("@0 +"+str(accept_val)+" ")
for i in range(4):                                 ############# range of 3?
    hofstadter_tm.write("@"+clock_pos+" ")
hofstadter_tm.write("@0 +1 +1 ")
for i in range(38):
    hofstadter_tm.write("@"+clock_pos+" ")
#hofstadter_tm.write("# !"+clock_pos+'\n')
hofstadter_tm.write("!"+clock_pos+'\n')


print(states_dict)
print(alphabet_dict)
print(tape_val_dict)


on_clock = "@0 +"+clock_pos+" \"^accept$\" ?"+str(accept_val)+" " 
running_check = "@0 +"+str(machine_state)+" \"^running$\" "

line_count += 1
hofstadter_tm.write(on_clock+"@0 @0 @0 @0 @0 +"+str(machine_state)+" # !"+str(line_count)+'\n')

for t in range(tape_length):
    tape_check = "@0 +"+str(current_tape_pos)+" \"^t"+str(t)+"$\" ?"+str(2*(t+1))+" "
    print_curr_read = "@0 +"+str(2*(t+1)+1)+" # "
    s: state
    for i, s in enumerate(states):
        state_check = "@0 +"+str(current_state)+" \"^"+s.state_name+"$\" ?"+str(first_state_name+i)+" "
        accept_reject_on_finish = None
        if s.is_accept:
            accept_reject_on_finish = accept_val
        else:
            accept_reject_on_finish = reject_val
        for j, c in enumerate(alphabet):
            character_check = "@0 +"+str(2*(t+1)+1)+" \"^"+c+"$\" ?"+str(first_alphabet+j)+" "
            if c in [x.reading_str for x in s.transitions_from]:
                k = [x.reading_str for x in s.transitions_from].index(c)
                print_curr_state = "@0 +"+str(current_state)+" # " #    print_curr_state+print_curr_read+
                #trans_write = "@0 +"+str(alphabet_dict[s.transitions_from[k].writing_str])+" # @"+str(tape_val_dict[str(t)])+' '
                trans_write = "@0 +"+str(alphabet_dict[s.transitions_from[k].writing_str])+" @"+str(tape_val_dict[str(t)])+' '
                #trans_to_state = "@0 +"+str(states_dict[s.transitions_from[k].to_state])+" # @"+str(current_state)+' '
                trans_to_state = "@0 +"+str(states_dict[s.transitions_from[k].to_state])+" @"+str(current_state)+' '
                trans_move = None
                line_count += 1
                repeat = " !"+str(line_count)+'\n'
                if s.transitions_from[k].movement == "RIGHT":
                    if t == tape_length - 1: # If we are at the last tape position
                        #trans_move = "@0 +"+str(tape_val_dict[str(t)])+" # @"+str(current_tape_pos)
                        trans_move = "@0 +"+str(tape_val_dict[str(t)])+" @"+str(current_tape_pos)
                    else: # We can indeed move to the right
                        #trans_move = "@0 +"+str(tape_val_dict[str(t)]+1)+" # @"+str(current_tape_pos)
                        trans_move = "@0 +"+str(tape_val_dict[str(t)]+1)+" @"+str(current_tape_pos)
                else:
                    if t == 0: # If we are at the first tape position
                        #trans_move = "@0 +"+str(tape_val_dict[str(t)])+" # @"+str(current_tape_pos)
                        trans_move = "@0 +"+str(tape_val_dict[str(t)])+" @"+str(current_tape_pos)
                    else: # We can indeed move to the left
                        #trans_move = "@0 +"+str(tape_val_dict[str(t)]-3)+" # @"+str(current_tape_pos)
                        trans_move = "@0 +"+str(tape_val_dict[str(t)]-3)+" @"+str(current_tape_pos)
                
                #hofstadter_tm.write(on_clock+tape_check+state_check+character_check+running_check+print_curr_state+print_curr_read+trans_write+trans_to_state+trans_move+repeat) # Maybe we should have more than one, so that we can assign all values together (one immediately following the other)
                hofstadter_tm.write(on_clock+tape_check+state_check+character_check+running_check+trans_write+trans_to_state+trans_move+repeat)
            else:
                line_count += 1
                repeat = " !"+str(line_count)+'\n'
                #hofstadter_tm.write(on_clock+tape_check+state_check+character_check+running_check+print_curr_state+print_curr_read+"@0 +"+str(accept_reject_on_finish)+" # @"+str(machine_state)+repeat)
                hofstadter_tm.write(on_clock+tape_check+state_check+character_check+running_check+"@0 +"+str(accept_reject_on_finish)+" @"+str(machine_state)+repeat)



    #-- Printing line data
    # If at the actual tape position, print the current state
    line_count += 1
    hofstadter_tm.write(on_clock+tape_check+"@0 +"+str(current_state)+" # !"+str(line_count)+'\n')
    # Always print the tape value
    line_count += 1
    hofstadter_tm.write(on_clock+"@0 @0 @0 @0 @0 +"+str(2*(t+1)+1)+" # !"+str(line_count)+'\n')
    
line_count += 1
hofstadter_tm.write(on_clock+"@0 @0 @0 @0 @0 +1 # !"+str(line_count)+'\n')

hofstadter_tm.write("tm_values/new_line.txt\n")
line_count += 1

hofstadter_tm.write(running_check + " ?0 +"+str(machine_state)+" +"+str(line_count)+' ')
for i, t in enumerate(tape_val_dict):
    hofstadter_tm.write('+'+str(tape_val_dict[t])+' ')
hofstadter_tm.write(" tm_out.txt")
line_count += 1


hofstadter_tm.close()
my_tm.close()

# Check that a string matches exactly : ^(ab)$