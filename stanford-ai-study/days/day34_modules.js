window.STUDY_DAY = {
  "day": 34,
  "date": "2026-10-29",
  "course": "CS231N · Spring 2026",
  "title": "Deep Learning for Computer Vision",
  "subtitle": "CNN, ResNet/transfer learning, Vision Transformer, self-supervised/generative vision을 1시간 핵심 + Deep Dive 구조로 정리한다.",
  "systemPosition": "Extension · Vision & Representation Learning",
  "systemMapping": "시각 모델 자체보다 representation learning, transfer, multimodal 확장 원리를 익혀 이미지·계측·공정 신호를 다루는 관점을 넓힌다.",
  "progressKey": "stanford-study-day34-progress-v3",
  "pcFile": "day34_2026-10-29_pc.html",
  "mobileFile": "day34_2026-10-29_mobile.html",
  "sourceLinks": [
    {"label": "CS231N Spring 2026", "url": "https://cs231n.stanford.edu/"},
    {"label": "CS231N Schedule", "url": "https://cs231n.stanford.edu/schedule.html"}
  ],
  "modules": [
    {
      "sourceLabel": "Lectures 5–6 · CNN & Architectures",
      "title": "Convolution에서 ResNet까지",
      "core": ["Convolution은 local receptive field와 weight sharing으로 이미지 구조를 활용한다.", "깊은 network는 residual connection을 통해 optimization을 안정화한다.", "Transfer learning은 큰 dataset에서 배운 representation을 작은 target task에 재사용한다."],
      "easy": "이미지 전체를 한 번에 보는 대신 작은 창을 움직이며 같은 검출기를 반복 적용하는 것이 convolution의 핵심 직관이다. ResNet은 깊어져도 원래 정보가 흐를 지름길을 만든다.",
      "professor": "CS231N은 선형 classifier와 backprop을 이해한 뒤 CNN으로 넘어가며, 이후 AlexNet/VGG/ResNet을 통해 architecture가 어떻게 깊어지고 학습이 안정화됐는지 보여준다. Transfer learning은 실제 프로젝트에서 scratch 학습보다 훨씬 자주 쓰이는 전략이다.",
      "practical": "웨이퍼/SEM 이미지처럼 label이 제한적이라면 pretrained backbone을 feature extractor로 쓰고 작은 head만 학습하는 접근부터 시작한다. 단, source domain과 target domain 차이가 크면 transfer 이득이 줄 수 있어 validation이 필요하다.",
      "terms": [["Convolution", "지역 패턴에 같은 filter를 반복 적용하는 연산"], ["Residual connection", "입력을 변환 결과에 더하는 skip path"], ["Transfer learning", "기존 task에서 학습한 representation을 새 task에 재사용하는 방법"]],
      "quiz": [["CNN의 weight sharing이 주는 장점은?", "위치마다 별도 parameter를 두지 않아 parameter 수를 줄이고 지역 패턴을 재사용할 수 있다."], ["Label이 적은 vision task에서 scratch 학습보다 먼저 검토할 것은?", "Pretrained model을 이용한 transfer learning 또는 fine-tuning이다."]]
    },
    {
      "sourceLabel": "Lecture 8 · Attention & Transformers",
      "title": "Vision Transformer와 Tokenization",
      "core": ["Vision Transformer는 이미지를 patch token sequence로 바꿔 self-attention을 적용한다.", "Image patch 크기와 tokenization은 계산량과 local detail 보존 사이 trade-off를 만든다.", "CNN의 inductive bias가 줄어드는 대신 data/compute 요구가 커질 수 있다."],
      "easy": "사진을 작은 타일로 잘라 각 타일을 문장의 단어처럼 취급하고, 어떤 타일끼리 관련 있는지 attention으로 보는 방식이 ViT의 기본 아이디어다.",
      "professor": "2026 CS231N은 RNN 이후 attention/Transformer를 다루고 ViT를 연결한다. 여기서 핵심은 Transformer가 text 전용 구조가 아니라 tokenization만 정의하면 여러 modality에 적용될 수 있다는 점이다.",
      "practical": "공정 시계열이나 이미지도 tokenization/patching을 어떻게 정의하느냐가 representation 품질과 비용을 좌우한다. 원시 고해상도 데이터를 그대로 넣기보다 domain-relevant crop, patch, feature compression을 검토한다.",
      "terms": [["Vision Transformer", "이미지 patch를 token으로 처리하는 Transformer 기반 vision model"], ["Patch embedding", "이미지 patch를 vector token으로 변환하는 단계"], ["Inductive bias", "모델 구조가 미리 내장한 문제 가정"]],
      "quiz": [["ViT에서 patch size를 작게 하면 일반적으로 어떤 변화가 생기는가?", "Token 수가 늘어 fine detail은 보존되지만 attention 계산량과 memory가 커진다."], ["Transformer를 vision에 쓸 수 있는 이유는?", "이미지를 token sequence로 표현하면 self-attention 구조를 modality와 무관하게 적용할 수 있기 때문이다."]]
    },
    {
      "sourceLabel": "Lecture 12 · Self-supervised Learning",
      "title": "Label 없이 Representation 배우기",
      "core": ["Self-supervised learning은 label 대신 data 자체에서 학습 목표를 만든다.", "Contrastive learning은 같은 instance의 augmentation을 가깝게, 다른 sample을 멀게 만드는 식으로 representation을 학습할 수 있다.", "좋은 representation은 downstream label이 적어도 성능을 높일 수 있다."],
      "easy": "정답지를 주지 않고 같은 사진을 조금 다르게 변형해도 같은 물체라고 알아보게 훈련하는 방식이다. 모델이 먼저 세상을 보는 법을 배우고 나중에 적은 정답으로 task를 익힌다.",
      "professor": "CS231N은 supervised classification 이후 self-supervised representation으로 확장한다. 이는 label 비용이 큰 실제 domain에서 중요한 흐름이며 최근 multimodal pretraining의 기반이기도 하다.",
      "practical": "공정 이미지와 sensor snapshot은 label이 적지만 raw data는 많을 수 있다. Self-supervised pretraining 후 defect/metric prediction을 fine-tune하면 label 효율을 개선할 가능성이 있다. 다만 pretext task가 실제 downstream 변동을 보존하는지 검증해야 한다.",
      "terms": [["Self-supervised learning", "Label 없이 입력 자체에서 supervision 신호를 만드는 학습"], ["Contrastive learning", "Positive pair를 가깝게, negative pair를 멀게 만드는 representation 학습"], ["Augmentation", "의미를 유지하며 입력을 변형하는 기법"]],
      "quiz": [["Self-supervised learning이 label이 적은 domain에서 유용한 이유는?", "대량의 unlabeled data로 representation을 먼저 배운 뒤 적은 label로 fine-tuning할 수 있기 때문이다."], ["Augmentation을 잘못 고르면 어떤 문제가 생기는가?", "Task에 중요한 신호까지 제거해 잘못된 invariance를 학습할 수 있다."]]
    },
    {
      "sourceLabel": "Lectures 13–18 · Generative, Multimodal & World Models",
      "title": "생성 모델에서 Vision-Language까지",
      "core": ["VAE/GAN/autoregressive/diffusion은 서로 다른 방식으로 data distribution을 모델링한다.", "Vision-language model은 이미지와 text representation을 공동 공간이나 cross-attention으로 연결한다.", "World model은 단순 인식보다 future state와 dynamics를 표현하려는 방향이다."],
      "easy": "분류기는 사진에 이름을 붙이는 데 집중하지만 생성 모델은 비슷한 사진이 어떻게 만들어지는지까지 배우려 한다. 여기에 언어를 연결하면 이미지를 설명하고 질문에 답하는 multimodal system으로 확장된다.",
      "professor": "2026 일정 후반은 diffusion, 3D vision, vision-language, world modeling, human-centered AI로 이어진다. 즉 vision course가 단순 classification을 넘어 generative and interactive intelligence로 확장되는 흐름을 보여준다.",
      "practical": "공정 agent가 이미지 evidence를 다룰 때 vision encoder 결과를 text summary로만 축약하면 정보 손실이 클 수 있다. 이미지 embedding, structured measurement, provenance를 함께 보존하는 multimodal evidence schema를 고려한다.",
      "terms": [["Diffusion model", "Noise를 점진적으로 제거하며 data를 생성하는 모델 계열"], ["Vision-language model", "시각과 언어 representation을 함께 학습하거나 결합하는 모델"], ["World model", "환경 상태와 변화 dynamics를 내부적으로 모델링하는 접근"]],
      "quiz": [["Vision-language model이 단순 image classifier보다 확장되는 지점은?", "이미지와 언어를 공동 표현해 설명·질의응답·reasoning 같은 task를 수행할 수 있다는 점이다."], ["Multimodal evidence를 text 한 줄로만 저장할 때 위험은?", "원본 시각 정보와 provenance가 사라져 추후 검증과 재해석이 어려워질 수 있다."]]
    }
  ]
};