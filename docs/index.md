---
title: ""
feature_image: "https://picsum.photos/1300/400?image=989"
feature_text: |
  ## Policy Graphs and Intention: answering ’why’ and ’how’ from a telic perspective
  Victor Gimenez-Abalos<sup>*1</sup>, Sergio Alvarez-Napagao<sup>1,2</sup>, Adrián Tormos<sup>1</sup>, <br> Ulises Cortés<sup>1,2</sup>, Javier Vazquez-Salceda<sup>1</sup>
  <small>
    <br>
    <sup>*</sup>Corresponding author <victor.gimenez@bsc.es>
    <br>
    <sup>1</sup>Barcelona Supercomputing Center
    <br>
    <sup>2</sup>Universitat Politècnica de Catalunya
  </small>
  
---


{% include button.html text="Paper" link="" color="#4f2121"  %} {% include button.html text="Code" link="https://github.com/hpai-bsc/pgeon" color="#113662"  %} {% include button.html text="BlueSky" link="https://bsky.app/profile/hpai.bsky.social" color="rgb(32, 139, 254)" %}  {% include button.html text="Linkedin" link="https://www.linkedin.com/company/hpai" color="#0a66c2" %}

### Abstract

> Agents are a special kind of AI-based software in that they interact in complex environments and have increased potential for emergent behaviour. 
Explaining such behaviour is key to deploying trustworthy AI, but the increasing complexity and opaque nature of many agent implementations makes this hard. 
In this work, we reuse the Policy Graphs method --which can be used to explain opaque agent behaviour-- and enhance it to query it with hypotheses of desirable situations. These hypotheses are used to compute a numerical value to examine agent intentions at any particular moment, as a function of how likely the agent is to bring about a hypothesised desirable situation. We emphasise the relevance of how this approach has full epistemic traceability, and each belief used by the algorithms providing answers is backed by specific facts from its construction process.
We show the numeric approach provides a robust and intuitive way
to provide telic explainability (explaining current actions from the perspective of bringing about situations), and allows to evaluate the interpretability of behaviour of the agent based on the explanations; and it opens the door to explainability that is useful not only to the human, but to an agent.

### Video explanation

<iframe width="502" height="282" src="https://www.youtube.com/embed/FOZkfVnE3vA" title="pgs" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Intention Policy Graphs (IPG)

IPGs are a simple model for understanding telic (that is, long-term) agent behaviour. The gist is: if an explainee would 
understand that an agent acts to achieve something apparently desirable, then providing responses that summarise behaviour
as 'bringing about' such achievement can explain actions. 

Rather than assume that the agent tracks these desirable things, we approach it from an architecture-agnostic perspective:
What is needed to know if agent behaviour will bring about some desirable state? Motivated by folk-psychology, we
consider the eponymous intentions, which are the result of the desire to achieve something together with a belief it can
be attained.

In this work, we operationalise intention as the probability that a desire be fulfilled in the future of a given state.
We use Policy Graphs (PG) as a model to estimate probabilities of actions and transitions (P(s'|a,s), P(a|s)) such that
we can compute the probability of any trajectory culminating on a desirable transition in the graph, for any possible
state: for a desire `d`, and a state `s`, there is an intention `I_d(s)` (which follows axioms of probability).

### Evaluation, metrics, and XAI

In order to evaluate that an intention occurs, we impose a commitment threshold `C` as the minimum intention that a state
needs in order to say that an intention is _attributed_ to the agent in a state. 
This doubles as a trade-of between interpretability and reliability. At higher `C`, the explainee is skeptic 
toward explanations, intentions are less often attributed (and hence part of answers to explainability), but they are
more frequently intentions that come to be fulfilled.

We use this intention to answer questions such as: 
* What does the agent intend to do at state `s`? Any intention that is _attributed_ in `s` (`I_d(s)>C`).
* Why would it do `a` at `s`? The intentions attributed in `s` that are expected to increase by using `a`
* How would the agent fulfill `d` from `s`? A plausible sequence of actions and states the PG believes will occur such 
that `d` is brought about, starting at `s`.

### Cite as

```
@inproceedings{gimenez_intention_aware_2025,
author = {Gimenez-Abalos, Victor and Alvarez-Napagao, Victor and Tormos, Adrian and Cortés, Ulises and Vázquez-Salceda, Javier},
title = {Policy Graphs and Intention: answering ‘why’ and ‘how’ from a telic perspective},
year = {2025},
isbn = {},
publisher = {International Foundation for Autonomous Agents and Multiagent Systems},
address = {Richland, SC},
abstract = {},
booktitle = {Proceedings of the 24rd International Conference on Autonomous Agents and Multiagent Systems},
pages = {},
numpages = {},
keywords = {},
location = {Detroit, United States of America},
series = {AAMAS '25}
}
```