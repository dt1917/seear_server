# Seear소개
본 서비스는 배리어프리를 바탕으로한 사회공헌 서비스입니다. 대상은 시각장애를 갖고 있는 사람이며 시각적으로 처리하기 어려운 부분을 청각적 요소로 변환하여 서비스를 제공하는 것이 핵심 목적입니다. 예를들어 HTML에서 제공하는 ALT속성은 사진을 설명하는 용도로 제공되고 있으나 사진의 세부 내용이 적혀있는 기사는 한정적이고 실제 스크린리더는 페이지의 많은 광고로 인해 스크린리더의 역할을 다하고 있지 못합니다. 본 서비스는 이미지 자체를 직접 캡셔닝하여 읽어주며 어떠한 이미지라도 쉽게 접근할 수 있도록 합니다. 최종 목표은 시각적으로 얻을 수 있는 정보에 취약한 시각 또는 인지 장애인이 음성을 통해 비장애인과 동일한 수준의 정보를 습득하도록 하는 것입니다.
> 베리어프리란? 사회적 약자들의 사회 생활에 지장이 되는 물리적 장애물이나 심리적인 장벽을 없애기 위한 기술

# 실행시 필요한 파일
- .flaskenv
- BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth (S3)
- WORDMAP_coco_5_cap_per_img_5_min_word_freq (S3)

# Seear Architecture
<img width="500" alt="image" src="https://user-images.githubusercontent.com/56428918/174254708-e68b9ea6-5343-464d-a982-7cd651d50138.png">

# Seear AWS Architecture
<img width="500" alt="image" src="https://user-images.githubusercontent.com/56428918/174254546-0769b777-a176-46e0-9ce3-65d7e57b0233.png">

# Seear Panel
<img width="500" alt="image" src="https://user-images.githubusercontent.com/56428918/174249810-8b55e996-7846-4cdf-8590-104c6a24c6e3.png">

# 담당파트
|파트|프레임워크 및 라이브러리|이름|
|:---:|:---:|:---:|
|FrontEnd|Vue.js|최솔, 백지연|
|BackEnd|Flask|이재준, 한지수|
|ML&DL|Pytorch|조형서|
