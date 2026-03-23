Results
=======

Time Trial
----------

Our Romi robot was able to successfully navigate the course all 3 times in ~47 seconds per run. It recieved no environmental time modifiers. Demonstration: https://www.youtube.com/watch?v=C2cvVYkPYGg.

Discussion
----------

We were very satisfied with our robot's preformance. Achieving consistent reliability with fair speed was incredibly validating for our robot's fairly simplistic design. Of the obstacles the time trial couse presented, we expected shifting testing environments from the circle test course (just a black line circle on a white paper) to the newly printed time trial course would require some recalibration/retooling of our line sensors/drivers to accomodate the differences in light reflectivity. However, it ended up being suprisingly unimpactful to our preformance - doubly so considering a lack of sensor calibration as seen in the demo. For this santizied and stable environment, the lack of calibration was OK to omit, but in an improved rendition with more time, it would make sense to calibrate the sensors prior to deployment to allow for usage with a wider range of surfaces.

We were also initially daunted by the garage. Thanks to our robust line sensor functionality, we were also able to go without state-space estimation, which provided the additional benefit of reducing our overall time since the robot didn't need to preform complex positional calculations to orient itself in the absence of a guiding black line. For this we were able to depend solely on the bump sensor and encoder tracking to determine the right place to exit the garage, which worked to with very good efficiency and reliability. Again, for broader applicaiton in an improved model, including state space estimation expands the general use capacity of the robot, but for optimization in the time trial course, it seemed to see less value.

Apart from improvements to the current sensor suite on our Romi robot, future improvments could see bluetooth integration, which could possibly improve developement times by allowing for more direct access to the robot development with requiring the usb cable, and other groups seemed to experience good success with an ultrasonic sensor. Additionally, a counterweight on the back of the robot would've probably improved some of the rattling and overall jumpiness of the robot in accelerations/decelerations leading to faster and smoother runs.

Overall, we were very happy with the preformance of our robot and found the project to have enriched our understanding of electromechanical system control and design. 
