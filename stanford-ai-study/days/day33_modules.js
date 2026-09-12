window.STUDY_DAY = {
  "day": 33,
  "date": "2026-10-28",
  "course": "CS234 · Winter 2026",
  "title": "Reinforcement Learning",
  "subtitle": "MDP, value/Q-learning, policy gradient, offline/imitation/RLHF를 agent 의사결정 관점으로 연결한다.",
  "systemPosition": "Extension · Sequential Decision Making",
  "systemMapping": "한 번의 예측이 아니라 행동→결과→다음 상태가 이어지는 문제를 언제 RL로 정의해야 하는지 판단하는 날이다.",
  "progressKey": "stanford-study-day33-progress-v3",
  "pcFile": "day33_2026-10-28_pc.html",
  "mobileFile": "day33_2026-10-28_mobile.html",
  "sourceLinks": [
    {"label": "CS234 Winter 2026", "url": "https://web.stanford.edu/class/cs234/"},
    {"label": "CS234 Lecture Materials", "url": "https://web.stanford.edu/class/cs234/modules.html"}
  ],
  "modules": [
    {
      "sourceLabel": "Lecture Topics · MDP Planning",
      "title": "State, Action, Reward, Dynamics",
      "core": ["MDP는 state, action, transition dynamics, reward, discount로 순차 의사결정을 표현한다.", "좋은 RL 문제 정의는 reward보다 먼저 state가 충분한 정보를 담는지 확인해야 한다.", "모든 최적화 문제를 RL로 만들 필요는 없다."],
      "easy": "체스는 현재 보드 상태에서 수를 두면 다음 보드가 생기고, 이 과정이 반복된다. 한 수의 좋고 나쁨만이 아니라 앞으로 이어질 결과까지 고려해야 하므로 순차 의사결정이 된다.",
      "professor": "CS234는 RL을 다른 ML과 구분하는 핵심으로 interaction과 delayed consequence를 둔다. state/action/reward를 형식화할 수 있어야 어떤 algorithm을 선택할지도 논리적으로 결정할 수 있다.",
      "practical": "공정 recipe 추천이 단일 DOE 후보를 고르는 문제라면 constrained optimization/BO가 더 직접적일 수 있다. 여러 단계 recipe 조정이 다음 상태와 이후 선택에 영향을 주고 feedback이 연속적으로 누적될 때 RL 정의를 검토한다.",
      "terms": [["MDP", "Markov Decision Process, 순차 의사결정 문제의 표준 수학 모델"], ["State", "다음 의사결정에 필요한 현재 상황 표현"], ["Reward", "행동 결과의 선호를 수치화한 신호"]],
      "quiz": [["단발성 regression 문제를 RL로 만들 필요가 없는 이유는?", "행동-상태 전이와 장기 보상이라는 RL의 핵심 구조가 없기 때문이다."], ["State 정의가 불충분하면 생기는 문제는?", "같은 state 표현에서 실제 미래가 달라져 policy가 일관된 결정을 배우기 어렵다."]]
    },
    {
      "sourceLabel": "Lecture Topics · Value & Q-learning",
      "title": "Value Function과 Q-learning",
      "core": ["Value function은 현재 state 또는 state-action에서 기대되는 누적 return을 추정한다.", "Q-learning은 다음 행동을 직접 따라가지 않고 max Q target을 사용해 optimal action value를 학습하는 off-policy 방법이다.", "Function approximation을 쓰면 일반화가 가능하지만 안정성 문제가 생긴다."],
      "easy": "지금 선택 하나의 즉시 점수보다, 그 선택 이후 앞으로 받을 점수의 총합을 예상하는 것이 value다. Q는 '이 상황에서 이 행동을 하면 앞으로 얼마나 좋을까'를 묻는다.",
      "professor": "Tabular planning에서 policy evaluation을 이해한 뒤 model-free Q-learning으로 넘어가는 흐름은 dynamics를 모를 때 data로 value를 추정하는 방법을 보여준다. Deep RL에서는 이 target이 움직이기 때문에 안정화 기법이 중요해진다.",
      "practical": "공정 feedback data가 sparse하고 policy가 바뀌면 data distribution도 바뀐다. 과거 engineer decision log로 Q를 학습하더라도 unseen action 영역의 값을 과신하지 않도록 OOD/uncertainty와 action constraint가 필요하다.",
      "terms": [["Value function", "어떤 상태에서 기대되는 누적 보상의 가치"], ["Q-function", "상태-행동 쌍의 기대 누적 보상"], ["Off-policy", "현재 data를 만든 policy와 다른 target policy를 학습할 수 있는 성질"]],
      "quiz": [["Q(s,a)는 무엇을 의미하는가?", "상태 s에서 행동 a를 한 뒤 얻을 기대 누적 return이다."], ["Offline data에서 Q 값을 과대평가하기 쉬운 영역은?", "Data에 거의 없거나 관측되지 않은 action/state 영역이다."]]
    },
    {
      "sourceLabel": "Lecture Topics · Policy Gradient",
      "title": "Policy를 직접 최적화하기",
      "core": ["Policy gradient는 action value를 통해 policy parameter의 기대 return을 직접 증가시키는 방향을 추정한다.", "Stochastic policy는 exploration과 확률적 의사결정을 표현하기 쉽다.", "Gradient estimate의 variance가 커질 수 있어 baseline/advantage 같은 기법을 사용한다."],
      "easy": "Q-learning이 각 행동의 점수를 먼저 배우고 가장 좋은 행동을 고른다면, policy gradient는 '어떤 행동을 얼마나 자주 선택할지' 자체를 직접 조정한다.",
      "professor": "Policy search는 continuous action과 stochastic policy에서 자연스럽다. 하지만 data efficiency와 variance 문제가 있어 actor-critic 계열처럼 value estimator와 결합하는 방식이 널리 쓰인다.",
      "practical": "Recipe parameter가 연속적이라고 해서 바로 policy gradient가 답은 아니다. 안전 constraint와 sample cost가 매우 큰 공정에서는 simulator 품질, offline data coverage, safe exploration 가능성을 먼저 확인해야 한다.",
      "terms": [["Policy gradient", "Policy parameter를 기대 return 방향으로 직접 최적화하는 방법"], ["Advantage", "특정 행동이 상태의 평균적 행동보다 얼마나 더 좋은지 나타내는 값"], ["Actor-Critic", "Policy actor와 value critic을 함께 학습하는 구조"]],
      "quiz": [["Policy gradient가 continuous action에 자연스러운 이유는?", "Action distribution의 parameter를 직접 학습할 수 있기 때문이다."], ["실험 비용이 큰 실제 공정에서 online exploration이 위험한 이유는?", "학습을 위해 의도적으로 미지의 action을 시도하는 과정이 품질·안전 비용을 발생시킬 수 있기 때문이다."]]
    },
    {
      "sourceLabel": "Lecture Topics · Offline RL, Imitation & RLHF",
      "title": "기존 Data와 Human Feedback에서 배우기",
      "core": ["Imitation learning은 expert demonstration을 따라 policy를 학습한다.", "Offline RL은 새 환경 interaction 없이 고정 dataset으로 policy를 개선하려 한다.", "RLHF는 human preference 또는 feedback을 reward 신호로 변환해 policy를 조정하는 한 계열이다."],
      "easy": "운전 연습을 직접 도로에서 시행착오로 하는 대신 숙련 운전자의 기록을 보고 배우는 것이 imitation/offline 접근이다. 다만 기록에 없는 상황에서 무엇을 해야 하는지는 여전히 어렵다.",
      "professor": "CS234의 2026 일정은 imitation, human input, batch/offline RL을 한 흐름에서 다룬다. 공통 문제는 logged data가 특정 behavior policy의 결과라서 counterfactual action의 결과를 직접 관측하지 못한다는 점이다.",
      "practical": "과거 평가·DOE 기록을 학습에 쓰면 engineer selection bias와 coverage를 점검해야 한다. '선택되지 않은 후보'의 결과는 없으므로 모델이 추천하는 새로운 영역에 대해 conservative constraint와 human review가 필요하다.",
      "terms": [["Imitation learning", "Expert demonstration을 모방해 policy를 학습하는 방법"], ["Offline RL", "고정된 과거 dataset만으로 policy를 학습/개선하는 RL"], ["Behavior policy", "Dataset을 생성한 당시의 행동 선택 정책"]],
      "quiz": [["Offline RL의 핵심 어려움은?", "Dataset에 없는 action의 결과를 신뢰성 있게 평가하기 어렵다는 distribution shift 문제다."], ["과거 engineer 선택 기록에 selection bias가 생기는 이유는?", "이미 안전하거나 유망하다고 판단된 후보만 실제로 실행·관측되는 경향이 있기 때문이다."]]
    },
    {
      "sourceLabel": "Lecture Topics · Exploration",
      "title": "Exploration과 Safety",
      "core": ["Exploration은 더 좋은 action을 찾기 위해 불확실한 선택을 시도하는 과정이다.", "Bandit/RL에서는 exploitation과 exploration의 균형이 핵심이다.", "고위험 환경에서는 safe exploration 또는 simulation/offline evaluation이 선행되어야 한다."],
      "easy": "늘 가던 식당만 가면 실패는 적지만 더 좋은 식당을 발견하기 어렵다. 새 식당을 가면 정보는 얻지만 실패 가능성이 있다. 이 균형이 exploration-exploitation이다.",
      "professor": "Exploration을 단순 randomness로 이해하면 안 된다. uncertainty, information gain, regret 같은 기준으로 어떤 실험이 가치 있는지 판단한다. 실제 응용에서는 safety constraint가 exploration policy를 제한한다.",
      "practical": "DOE 추천은 정보 획득 가치가 있어도 공정 spec/장비 한계/품질 risk를 넘으면 실행할 수 없다. 따라서 uncertainty-aware acquisition과 hard constraint를 분리하고 engineer 승인까지 포함하는 구조가 필요하다.",
      "terms": [["Exploration", "불확실한 action을 시도해 새로운 정보를 얻는 행동"], ["Exploitation", "현재 가장 좋아 보이는 action을 선택하는 행동"], ["Regret", "최적 행동을 알았을 때와 비교한 누적 손실 개념"]],
      "quiz": [["Exploration을 단순 random action으로 보면 안 되는 이유는?", "정보 가치와 위험을 고려해 효율적으로 선택해야 하기 때문이다."], ["고위험 DOE에서 exploration 전에 필요한 것은?", "Hard constraint, OOD/uncertainty 평가, 가능하면 simulator/offline 검증과 human approval이다."]]
    }
  ]
};