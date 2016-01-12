"""
This represents a simple fuzzy logic controller for an AI rowing shell.
It calculates 'strategy' during a 2000 meter rowing race based on
how far into the race the boat is and the relative position of the nearest
competior's boat.

The actions the boat can take are:
    
        EASE_UP - row a little bit lighter to conserve energy.
        AS_IS - make no change, that is keep doing what its doing
        LENGTHEN_OUT - row a little bit longer (lengthen out the stroke) to gain a little speed without working harder
        P10 - take a 'power 10' which is 10 strokes at the absolute hardest.  often used to pass another boat
        SPRINT - all out sprint, almost always at the end of the race.

(C) 2016 Kevin Dahlhausen
This file is licensed under the GNU GPL.  Any version.

"""


import sys
sys.path.append("../src") # run w/out install


from fl.engine import Engine, Operator
from fl.variable import InputVariable, OutputVariable
from fl.term import Triangle, LeftShoulder, RightShoulder, Trapezoid
from fl.ruleblock import RuleBlock
from fl.mamdani import MamdaniRule


def simple_ai_boat():
        fe = Engine('simple-mamdani')

        
        """
        RELATIVE LOCATION

        ----------\    X       X      X       ------------
                   \  / \     / \    / \     /
                    \/   \   /   \  /   \   /   
                    /\    \ /     \/     \ /     
                   /  \    X      /\      X       
                  /    \  / \    /  \    / \       

         FAR        BEHIND           AHEAD       FAR
         BEHIND              ABOUT               AHEAD
                             EVEN
        """

        #shoulder break points in meters
        FAR_MAX=85.0
        FAR_MIN=60.0

        #behind/ahead points in meters
        BEHIND_AHEAD_MIN=66.0
        BEHIND_AHEAD_MIDPOINT=40.0
        BEHIND_AHEAD_MAX=14.0

        # about even magnitude - triangle membership 
        ABOUT_EVEN_MAGNITUDE=16.0


        relative_location = InputVariable('relative_location')
        relative_location.term['FAR_BEHIND'] = LeftShoulder('FAR_BEHIND', -FAR_MAX, -FAR_MIN)
        relative_location.term['BEHIND'] = Triangle('BEHIND', -BEHIND_AHEAD_MIN, -BEHIND_AHEAD_MIDPOINT, -BEHIND_AHEAD_MAX)
        relative_location.term['ABOUT_EVEN'] = Triangle('ABOUT_EVEN', -ABOUT_EVEN_MAGNITUDE, 0.0, ABOUT_EVEN_MAGNITUDE)
        relative_location.term['AHEAD'] = Triangle('AHEAD', BEHIND_AHEAD_MAX, BEHIND_AHEAD_MIDPOINT, BEHIND_AHEAD_MIN)
        relative_location.term['FAR_AHEAD'] = RightShoulder('FAR_AHEAD', FAR_MIN, FAR_MAX)
        fe.input['relative_location'] = relative_location
        



        # locations in a 2000 m piece in meters
        location = InputVariable('location')
        location.term['BEGINNING'] = LeftShoulder('BEGINNING', 500.0, 800.0)
        location.term['MIDDLE'] = Trapezoid('MIDDLE', 650.0, 800.0, 1500.0, 1600.0)
        location.term['END'] = RightShoulder('END', 1570.0, 1700.0)
        fe.input['location'] = location




        """
        ACTION:


        ------------\ ---------\ ----------------\  -------\  ---------
                     X          X                 \/        \/
                    / \        / \                /\        /\ 
         EASE_UP   /   \ AS   /   \    LENGTHEN  /  \ P10  /  \ SPRINT
                         IS
        """                                          

        # ACTION values are unit-less

        EASE_UP_MIN=20.0   
        EASE_UP_MAX=25.0

        AS_IS_MIN=20.0
        AS_IS_B=35.0
        AS_IS_C=70.0
        AS_IS_MAX=75.0

        LENGTHEN_MIN=70.0
        LENGTHEN_B=73.0
        LENGTHEN_C=77.0
        LENGTHEN_MAX=80.0

        P10_MIN=77.0
        P10_B=80.0
        P10_C=90.0
        P10_MAX=93.0

        SPRINT_MIN=90.0
        SPRINT_MAX=95.0

        action = OutputVariable('action', default=float('nan'))
        action.term['EASE_UP'] = LeftShoulder('EASE_UP', EASE_UP_MIN, EASE_UP_MAX)
        action.term['AS_IS'] = Trapezoid('AS_IS', AS_IS_MIN, AS_IS_B, AS_IS_C, AS_IS_MAX)
        action.term['LENGTHEN'] = Trapezoid('LENGTHEN', LENGTHEN_MIN, LENGTHEN_B, LENGTHEN_C, LENGTHEN_MAX)
        action.term['P10'] = Trapezoid('P10', P10_MIN, P10_B, P10_C, P10_MAX)
        action.term['SPRINT'] = RightShoulder('SPRINT', SPRINT_MIN, SPRINT_MAX)
        fe.output['action'] = action




        
        ruleblock = RuleBlock()

        ruleblock.append(MamdaniRule.parse('if location is BEGINNING then action is AS_IS', fe))

        ruleblock.append(MamdaniRule.parse('if location is MIDDLE and relative_location is FAR_BEHIND then action is LENGTHEN', fe))
        ruleblock.append(MamdaniRule.parse('if location is MIDDLE and relative_location is BEHIND then action is P10', fe))
        ruleblock.append(MamdaniRule.parse('if location is MIDDLE and relative_location is ABOUT_EVEN then action is P10', fe))
        ruleblock.append(MamdaniRule.parse('if location is MIDDLE and relative_location is AHEAD then action is LENGTHEN', fe))
        ruleblock.append(MamdaniRule.parse('if location is MIDDLE and relative_location is FAR_AHEAD then action is AS_IS', fe))
 

        ruleblock.append(MamdaniRule.parse('if location is END and relative_location is FAR_BEHIND then action is LENGTHEN', fe))
        ruleblock.append(MamdaniRule.parse('if location is END and relative_location is BEHIND then action is SPRINT', fe))
        ruleblock.append(MamdaniRule.parse('if location is END and relative_location is ABOUT_EVEN then action is SPRINT', fe))
        ruleblock.append(MamdaniRule.parse('if location is END and relative_location is AHEAD then action is SPRINT', fe))
        ruleblock.append(MamdaniRule.parse('if location is END and relative_location is FAR_AHEAD then action is AS_IS', fe))


        fe.ruleblock[ruleblock.name] = ruleblock
        
        fe.configure(Operator())
        return fe


aib = simple_ai_boat()




def get_fuzzy_output( ai_boat_distance_in, other_boat_distance_in):
    """ return (action, location, relative_location) fuzzy variables for the given AI boat distance in and nearest competitor distance into the race
     (returns the fuzzy variables to the gui demo can show the complete set membership values)
    """

    rl_raw = ai_boat_distance_in - other_boat_distance_in
    relative_location = aib.input['relative_location']
    location = aib.input['location']
    action = aib.output['action']
    relative_location.input = rl_raw
    location.input = ai_boat_distance_in
    aib.process()
    return action, location, relative_location

