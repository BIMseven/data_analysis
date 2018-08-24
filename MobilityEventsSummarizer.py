import tkinter as tk
from tkinter import filedialog
from statistics import median
import sys

################################################################CLASSES:

class parsedCollision():

    def __init__( self, line ):
        split_by_commas = line.split( "," )
##        split_by_close_paren = line.split
        

class completedCourse():

    def __init__( self, course_name ):
        self.name = course_name
        self.times_off_course = 0
        self.total_time_off_course = 0
        self.pulses = 0
        self.total_time_off_course_after_pulse = 0
        self.completion_time = -1
        self.buttons_pressed = 0
        self.total_collisions = 0
        self.foot_collisions = 0        
        self.hand_collisions = 0
        self.head_collisions = 0
        self.time_off_course_after_pulse = 0        
        self.sec_off_course = 0
        self.sec_pulsed = 0
        self.did_pulse = False
        self.config_string = ""
    
    def parse_event_line( self, event_line ):

        time = float( event_line.split( "," )[-1] )
                
        if event_line.startswith( "Off course" ):            
            self.sec_off_course = time
            self.did_pulse = False

        elif event_line.startswith( "Pulse" ):     
            if self.sec_off_course == 0:
                return       
            self.did_pulse = True
            self.sec_pulsed = time            

        elif event_line.startswith( "Back" ):
            if self.sec_off_course == 0:
                return
            self.times_off_course += 1
            self.total_time_off_course += time - self.sec_off_course            
            time_since_pulse = time - self.sec_pulsed
            
            if self.did_pulse:
                self.pulses += 1
                self.total_time_off_course_after_pulse += time - self.sec_pulsed
                        
        elif event_line.startswith( "collide" ):
            collision = parsedCollision( event_line )
            collider_name = event_line.split( "*" )[2]
            if collider_name.endswith( "RH" ) or collider_name.endswith( "LH" ):
                self.hand_collisions += 1
            elif collider_name.endswith( "LF" ) or collider_name.endswith( "RF" ):
                self.foot_collisions += 1
            elif collider_name.endswith( "EYE" ):
                self.head_collisions += 1            
            self.total_collisions += 1
            
        elif event_line.startswith( "pressed" ):
            self.buttons_pressed += 1

########################################################################
    
# Ask user for input filenames and then open them
root = tk.Tk()
root.withdraw()

print( "Now select events file" )

####################################################REAL:
events_filepath = filedialog.askopenfilename()
###################################################DEBUG:
##events_filepath = "recorded_events_8-10-2018_9am.csv" 
#####################################################

if events_filepath == "":
    sys.exit( "Bad filepaths" )


events_file = open( events_filepath, "r" )

print( "selected events file: %s" % events_filepath )


##### Parse events file:
course = None
completed_courses = list()
is_navigating = False
second_started = 0
config = ""

while True:
    events_line = events_file.readline()
    if events_line is ""  or  events_line is None:        
        break;

    if events_line.startswith( "Loaded" ):     
        components = events_line.split( "," )        
        course_name = components[0].split( " " )[1]
        course = completedCourse( course_name )
        is_navigating = False

    elif events_line.startswith( "{" ):
        config = "\n{\n"        
        while True:
            events_line = events_file.readline()
            if events_line.startswith( "}" ):
                break;
            config += events_line;
        config += "}\n"
        
    elif events_line.startswith( "Subject navigating course: True" ):
        is_navigating = True
        second_started = float( events_line.split( "," )[1] )

    elif not is_navigating:
        continue;

    elif events_line.startswith( "Subject navigating course: False" ):        
        second_finished = float( events_line.split( "," )[1] )
        course.completion_time = second_finished - second_started
        course.config_string = config
        completed_courses.append( course )
        is_navigating = False
        
    else:
        course.parse_event_line( events_line )
#####

output_filepath = events_filepath[:-4] + "_summary.txt"
output_file = open( output_filepath, "w" )


##### Summarize events:

num_completed_courses = len( completed_courses )
total_collisions = 0
total_hand_collisions = 0
total_head_collisions = 0
total_foot_collisions = 0
total_times_off_course = 0
total_buttons_pressed = 0
median_completion_time = 0
median_time_off_course = 0


completion_times = list()
off_course_times = list()

for i in range( 0, num_completed_courses ):
    course = completed_courses[i]
    completion_times.append(course.completion_time)
    off_course_times.append(course.total_time_off_course)
    total_collisions += course.total_collisions
    total_hand_collisions += course.hand_collisions
    total_head_collisions += course.head_collisions
    total_foot_collisions += course.foot_collisions
    total_times_off_course += course.times_off_course
    total_buttons_pressed += course.buttons_pressed 


median_completion_time = median(completion_times)
median_time_off_course = median(off_course_times)

output_file.write( "-------------------------------------------\n" )
output_file.write( "Summary\n" )
output_file.write( "-------------------------------------------\n\n" )
output_file.write( "Completed courses: " )
output_file.write( str( num_completed_courses ) )
output_file.write( "\n" )
output_file.write( "Median course time: " )
output_file.write( "{:.3f}".format( median_completion_time ) )
output_file.write( "\n" )
output_file.write( "Median time spent off course: " )
output_file.write( "{:.3f}".format( median_time_off_course ) )
output_file.write( "\n" )
output_file.write( "Total times off course: " )
output_file.write( str( total_times_off_course ) )
output_file.write( "\n" )
output_file.write( "Total buttons pressed: " )
output_file.write( str( total_buttons_pressed ) )
output_file.write( "\n" )
output_file.write( "Total foot collisions: " )
output_file.write( str( total_foot_collisions ) )
output_file.write( "\n" )
output_file.write( "Total hand collisions: " )
output_file.write( str( total_hand_collisions ) )
output_file.write( "\n" )
output_file.write( "Total head collisions: " )
output_file.write( str( total_head_collisions ) )
output_file.write( "\n\n\n-------------------------------------------\n" )
output_file.write( "Breakdown\n" )
output_file.write( "-------------------------------------------\n\n" )

for i in range( 0, num_completed_courses ):
    course = completed_courses[i]
    output_file.write( "Course name: " )
    output_file.write( course.name )
    output_file.write( course.config_string )
    output_file.write( "\nTotal course time: " )
    output_file.write( "{:.3f}".format(  course.completion_time ) )
    output_file.write( "\nTimes off course: " )
    output_file.write( str( course.times_off_course ) )
    output_file.write( "\nTotal time off course: " )
    output_file.write( "{:.3f}".format( course.total_time_off_course ) )
    output_file.write( "\nTimes pulsed: " )
    output_file.write( str( course.pulses ) )
    output_file.write( "\nTotal time off course after pulse: " )
    output_file.write( "{:.3f}".format(  course.total_time_off_course_after_pulse ) )
    output_file.write( "\nButtons pressed: " )
    output_file.write( str( course.buttons_pressed ) )
    output_file.write( "\nFoot collisions: " )
    output_file.write( str( course.foot_collisions ) )
    output_file.write( "\nHand collisions: " )
    output_file.write( str( course.hand_collisions ) )
    output_file.write( "\nHead collisions: " )
    output_file.write( str( course.head_collisions ) )
    if i < num_completed_courses - 1:
        output_file.write( "\n\n" )
    
    
events_file.close()
output_file.close()

input( "Success!  Press Enter to close program" )            
