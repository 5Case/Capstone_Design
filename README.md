# Visual Object Tracking 성능 개선(SiamRPN)
### 소프트웨어융합캡스톤디자인 2022-1
### by KyeongWoo Kim

--------

## Overview
객체 추적(Object Tracking)은 비디오 영상에서 시간에 따라 움직이는 물체 또는 여러 개의 물체들의 위치 변화를 추적하는 기술이다.
이 Object Tracking은 영상 보안, 영상 통화, 교통 통제, 증강 현실, 로보틱스, 비디오 분석, 자율주행 자동차 등 동영상을 이용하는 
다양한 응용 분야에서 활용될 수 있기 때문에 오래전부터 많은 연구가 수행되고 있다. 이와 같이 다양한 응용 분야에 활용되는 만큼 Tracking을 
실패하지 않고 정확하게 예측하는 것이 중요하다. 이번 캡스톤디자인을 통해 tracker, 특히 SiamRPN의 tracking 성능을 높여보고자 한다.

--------

## Architecture
![image](https://user-images.githubusercontent.com/87515234/173172305-ab51766e-97de-43f0-b433-3e258f41a073.png)

SiamRPN의 tracking은 추적하고자 하는 target이 담긴 frame의 127x127 크기의 sub image인 Template Frame과 이후의 frame에서 추적하고자
하는 target이 담긴 255x255 크기의 sub image인 Detection Frame의 pair-wise correlation을 통해 이뤄진다. 
SiamRPN은 OTB pretrained model을 사용했다. 
**Tracker: SiamRPN

--------

## Process & Evaluation Methods
![image](https://user-images.githubusercontent.com/87515234/173172428-50687c5b-9180-4bee-b4c2-f84f53e1b82e.png)

**Process1**
기존 SiamRPN은 tracking이 종료될 때까지 첫 번째 frame의 target sub image를 Template Frame으로 고정한다. 영상에서 객체는 시간(frame)에
따라 움직이고 있고, 따라서 target의 특정 부분만을 가리키고 있는 단일 frame을 template frame으로 고정한다면 tracking에 실패할 가능성이
높아질 것이다. 첫 번째 과정은 Template Frame과 Detection Frame 간의 tracking 결과 score가 threshold보다 낮아지면 Template Frame을
교체하는 방식으로, Frame마다 바뀌는 target 모양에 대처하기 위한 실험이다. 즉, Template Frame을 교체했을 때의 성능을 측정하고자 한다.

**Process2**
두 번째 과정은 Template Frame을 교체하는 방식만을 사용하는 것이 아니라 Template Frame을 첫 번째 frame의 target sub image로 고정했을
때, 즉 기존의 SiamRPN의 tracking에 대한 결과도 같이 사용하여 과정1에 비해 더 좋은 성능을 얻기 위한 실험이다.

**Evaluation Methods**
원래 방식(Ground-Truth 사용)
![image](https://user-images.githubusercontent.com/87515234/173172725-5db8015c-d343-479b-8177-4d0d8c4fbd35.png)
수정 방식(Ground-Truth 미사용)
![image](https://user-images.githubusercontent.com/87515234/173172728-ec6f5b05-9546-4fe9-947f-e22a41e7a49a.png)

Evaluation Methods로는 VOT Challenge의 vot evaluation toolkit이 존재한다. 이 toolkit의 주요 지표로는 accuracy(average overlap),
robustness가 존재하는데, accuracy는 model이 예측한 predicted box와 ground-truth간의 overlap의 평균이고, robustness는 failures 수와
연관된 지표이다. Accuracy는 높을수록, robustness는 낮을수록 좋다. 기존 vot evaluation toolkit은 predicted box와 ground-truth가
겹치는 Overlap을 계산하여 그 값이 0이면 Tracking을 실패한 것으로 보고 Failures 수를 증가시키고, Accuracy 계산에는 추가하지 않는다.
또한 Tracking이 실패하면 실패한 시점부터 5 Frame을 evaluation에 반영하지 않고, 그 이후의 Frame을 Ground-Truth로 초기화하여 다시 
Tracking을 하여 evaluation 하는 구조이다. 하지만 실제 세계에서 Tracking을 한다면 Ground-Truth는 존재하지 않을 것이고, 따라서
사용할 수도 없다. 이번 과제에서는 Ground-Truth를 사용하는 기존의 방식을 수정하여, 첫 Frame만 Ground-Truth로 초기화(evaluation에
반영되지 않음)하고 Tracking을 실패하더라도 모든 Frame에 대해 오직 SiamRPN이 에측한 box에 대해서만 evaluation을 진행했다.

**Dataset**
VOT 2016
![image](https://user-images.githubusercontent.com/87515234/173172798-5d63a5d6-ef8d-4980-b723-ef6a2ee92da6.png)
VOT Challenge의 dataset으로 연도별로 sequence가 다르며, occlusion, illumination change, object motion, object size change,
camera motion, unassigned 등 6가지 attributes를 가지고 있다.

--------

## Results

Process 1 결과(table)
![image](https://user-images.githubusercontent.com/87515234/173172840-be0d2b9a-23a3-4ffe-ba72-42d5e44de70f.png)

Process 1 결과(plot)
![image](https://user-images.githubusercontent.com/87515234/173172841-3f8d3e47-d01b-4a96-be83-e777b416b06a.png)

Tracking 놓친 순간(Template Frame 고정)
![image](https://user-images.githubusercontent.com/87515234/173173010-5d0e92f7-dffa-495c-8e65-393e194ae7e7.png)

Tracking 놓친 후(Template Frame 고정)
![image](https://user-images.githubusercontent.com/87515234/173173013-b94ad56d-5144-4f5d-9c14-b7c5c6c7be06.png)

Tracking 놓친 순간(Template Frame 선택적)
![image](https://user-images.githubusercontent.com/87515234/173173034-bb10c80b-8861-4f67-a957-1ad0e0953f3a.png)

Tracking 놓친 후(Template Frame 선택적)
![image](https://user-images.githubusercontent.com/87515234/173173038-e8c857dc-04f4-4f48-b3d1-d1c074c08543.png)

Process 2 결과(table)
![image](https://user-images.githubusercontent.com/87515234/173172854-542efbe0-f9cd-4157-b78b-903486133c80.png)
Process 2 결과(plot)
![image](https://user-images.githubusercontent.com/87515234/173172856-42923273-83be-4c3a-b559-d47a64205f06.png)

Template Frame(fixed & selective) example 1
![image](https://user-images.githubusercontent.com/87515234/173173063-ea0369eb-8c11-4b91-942b-853738e0ada5.png)

Template Frame(fixed & selective) example 2
![image](https://user-images.githubusercontent.com/87515234/173173066-c9c3b0ed-b56d-4741-9efd-072ffa0d9fec.png)


## Results Videos

https://user-images.githubusercontent.com/87515234/173173491-f43e213d-f064-499e-be95-81d0cfa5d091.mp4

https://user-images.githubusercontent.com/87515234/173173485-35398d54-c1d9-4f21-b77e-479f83a30a7e.mp4

## Commands

**compare results**
'''
python compare_trackers.py --workspace_path workspace-dir --trackers tracker-id1 tracker-id2 tracker-id3 ... --sensitivity sensitivity

ex: python compare_trackers.py --workspace_path C:\Users\kgu26\capstone\workspace-dir --trackers SiamRPN SiamRPN_fix_template SiamRPN_selective_template SiamRPN_fixNselective_template --sensitivity -1
'''

**visualize results**
'''
python visualize_result.py --workspace_path workspace-dir --tracker tracker-id --sequence sequence-name

ex: python visualize_result.py --workspace_path C:/Users/kgu26/capstone/workspace-dir --tracker SiamRPN_fixNselective_template --sequence nature
'''

--------
