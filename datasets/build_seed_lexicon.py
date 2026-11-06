"""
Generates a comprehensive seed lexicon for Jessica's Cortex Tokenizer
Ensures that Jessica's vocabulary covers general English conversation, technical systems programming,
machine learning, hardware administration, and emotion/prosody semantics (2,500+ vocabulary size).
"""

import os
import re
import json
from pathlib import Path

# Common conversational words, verbs, adjectives, nouns, and technical vocabulary
WORD_GROUPS = [
    # Basic conversation & feelings
    "the be to of and a in that have i it for not on with he as you do at this but his by from they we say her she or an will my one all would there their what so up out if about who get which go me when make can like time no just him know take people into year your good some could them see other than then now look only come its over think also back after use two how our work first well way even new want because any these give day most us hello hi hey thanks thank please yes no great fine good bad wonderful fantastic amazing excellent perfect cool awesome super nice pleasant smooth fast slow steady calm quiet loud bright warm joyful playful excited serious curious grateful happy delighted eager sharp alert energetic",
    
    # Systems, hardware & OS
    "system hardware software computer machine device processor core thread memory ram vram disk drive storage filesystem folder directory path file binary executable script code program process service task daemon job thread worker queue socket port network interface adapter ethernet wifi connection router gateway subnet mask ip address localhost ping latency bandwidth packet frame byte bit kilobyte megabyte gigabyte terabyte clock frequency voltage wattage temperature thermal fan speed cooling heatsink chassis motherboard chipset bios uefi kernel driver interrupt register cache buffer queue stack heap paging virtual physical swap partition volume junction link symlink permission access privilege admin root user guest monitor display screen resolution pixel refresh rate gpu nvidia geforce rtx 4060 tensor cuda directx vulkan opengl windows powershell cmd terminal console event log journal audit telemetry metric status health diagnostic benchmark load usage utilization limit throttle threshold shutdown reboot sleep standby hibernate",
    
    # Networking & Web
    "network internet web protocol transmission control user datagram tcp ip udp http https websocket dns dhcp icmp broadcast multicast unicast routing table route hop traceroute firewall port forwarding proxy tunnel vpn ssl tls certificate handshake cipher signature encryption decryption symmetric asymmetric public private key hash sha256 md5 payload header frame socket endpoint connection client server peer host remote local cluster cloud sovereign isolated offline airgap firewall rule filter drop allow reject keepalive beacon broadcast handshake syn ack fin rst",
    
    # Audio, Speech & Voice
    "audio sound speech voice speech vocal timbre pitch formant acoustic frequency hertz decibel amplitude volume loudness gain tone intonation cadence prosody rhythm tempo meter rate speed duration pause breath resonance resonance harmonic overtone spectral centroid bandwidth energy root mean square rms envelope waveform sample sampling rate mono stereo channel microphone speaker headphone transducer synthesizer engine clone cloning zero shot reference audio phoneme diphthong vowel consonant syllable accent dialect expression mood feeling emotion warm playful excited calm serious curious whisper soft gentle assertive energetic crisp clear muffled echo reverb delay equalizer filter compression threshold ratio attack release",
    
    # Machine Learning & AI
    "artificial intelligence machine learning deep learning neural network model architecture layer weights bias parameter hyperparameter tensor matrix vector scalar gradient backpropagation forward backward pass loss cost error accuracy precision recall f1 score convergence divergence epoch batch step iteration learning rate optimizer adam adamw sgd momentum decay regularization dropout normalization layer norm batch norm activation function relu gelu sigmoid tanh softmax dot product attention causal self cross multi head key query value projection feedforward linear non linear transformer decoder encoder causal mask autoregressive token tokenization vocabulary subword embedding positional encoding sequence length context window prompt completion generation temperature sampling top k top p nucleus greedy beam search checkpoint snapshot state dict train validation test eval fine tuning zero shot few shot transfer learning representation latent space manifold dimensionality reduction pca clustering classification regression ranking search retrieval augmented generation rag vector database similarity cosine distance euclidean dot product index inverted index tf idf bm25 sparse dense hybrid",
    
    # Programming & Development
    "python rust javascript typescript c cpp csharp java go ruby php html css json yaml toml xml sql sqlite postgresql mongodb redis git repository commit branch merge rebase checkout stash push pull remote clone diff patch tag release build compile linker package library module framework sdk api interface class object method function procedure variable constant type integer float boolean string array list tuple dict dictionary map set hash table pointer reference struct enum trait interface polymorphism inheritance abstraction encapsulation recursion iteration loop while for if else switch case match exception error handler try catch throw finally assertion debug breakpoint profile benchmark unit test integration end to end mock stub patch fixture linter formatter ci cd deployment container docker kubernetes",
    
    # Logic, Math & Science
    "mathematics logic calculus algebra linear algebra geometry trigonometry probability statistics discrete combinatorics graph theory tree node edge directed acyclic matrix determinant inverse transpose eigenvalue eigenvector dot product cross product derivative integral differential partial gradient hessian divergence curl theorem axiom proof lemma corollary conjecture hypothesis empirical theoretical simulation numerical approximation float precision rounding error overflow underflow infinity nan boolean truth table and or not xor implication equivalence set subset union intersection difference complement relation function domain codomain range bijection injection surjection isomorphism homomorphism homomorphism",
    
    # General descriptive & actions
    "execute run start stop pause resume cancel abort terminate kill spawn fork launch dispatch handle process compute calculate measure evaluate analyze verify validate inspect check probe monitor audit inspect investigate trace track record log save store read write update delete modify replace insert append extract parse format render display visualize present communicate converse respond reply acknowledge confirm deny authorize reject grant revoke protect secure isolate sandbox defend optimize accelerate improve stabilize enhance refine scale distribute coordinate balance synchronize schedule queue defer trigger dispatch complete finish succeed fail retry recover fallback restore reset initialize configure setup install remove clean purge archive compress decompress encrypt decrypt verify sign hash authenticate identify observe understand decide reason think consider remember recall reflect adapt learn assist serve create construct build engineer develop implement deploy maintain operate guide explain clarify elaborate summarize inspect",

    # Additional vocabulary: nature, human conversation, technology, literature, science
    "action activity addition advance advantage affection agreement air alphabet answer apartment appearance appetite applause arrangement attitude autumn avenue background balance baseline bedroom behaviour belief border boundary branch breakfast breath breeze bridge brother builder cabinet calendar camera candidate captain carbon career castle ceiling celebration cell century ceremony certainty challenge champion channel chapter charity charm cheek choice circuit circumstance citizen classical climate cloth clothing coach coal coast coffee collection college column combination comfort commerce committee community companion comparison competition complaint complexity concept concert condition confidence conflict connection conscience conscious consciousness consent consequence consideration consistency constant consumer consumption container content context continent contrast contribution control convention conversation corner correction corruption cottage courage course court cover craft crash creator credit crisis criticism crown cruelty culture cupboard cure current curve customer custom cylinder damage danger darkness database dealer debate decade deceit decision declaration default defeat defense deficit definition degree delay delight demand democracy density deposit depth description desert desire despair dessert destination detection developer devil devotion diagram diamond diary diction difference difficulty dignity dimension dinner direction dirt discipline discovery discrimination disease disorder display dispute distinction distribution disturbance division doctor doctrine document domain dominant door double doubt draft dream dress drift driver drop drug dust duty eagle earth earthquake echo economy edition education effect effort election electricity element elevator emotion emphasis empire employee employment enclosure encouragement energy engine engineer enhance enterprise enthusiast entrance environment epidemic episode epoch equal equality equation equipment error escape essay estate esteem estimate event evening evidence evolution examination example excellence exception excitement excursion excuse execution executive existence expansion expedition expense experience experiment expert explanation explorer explosion export exposure extension external eye fabric facility factory failure faith fame family fancy farewell farmer fashion fault favor fear feather feature fee feedback feeder feeling female fence festival fiber fiction field fierce fight figure file filter final finance finger fire fireplace firearm firm fish fist fitness fixture flame flavor fleet flight floor flour flower fluid foam focus foe folder folk fondness food fool force forecast forest fork form format fortune foundation fraction fragment framework frame fraud freedom freeze frequency friend fright fruit fuel function fund funeral fur furnace furniture future gain galaxy gallery game garden garment gas gate gathering gauge gear general generator generation generous genius genuine gesture ghost giant gift girl glass glance glide globe glory glow glue goal god gold goods government governor grace grade gradual grain grammar grand granite grant graph graphic grasp grass gratitude gravity gray grease greeting grid grief grip ground group grove growth guarantee guard guidance guilt guitar gulf gun habit habitat hair half hammer hand handle hardness harmony harvest haste hatred haven hazard head health heart hearth heat heaven height heir helicopter hell helmet help herb heritage hero hide hill hint history hive hold hole hollow honesty honor hook hope horror horse hospital host hostage hotel hour house household hue hull human humanity humor hundred hunger hunt hunter hurricane hurt husband hymn hypothesis"
]

all_words = set()
for g in WORD_GROUPS:
    for w in g.split():
        clean = w.strip().lower()
        if len(clean) >= 2:
            all_words.add(clean)

# Load existing words from datasets/cortex_train.jsonl and cortex_v2_train.jsonl
for dataset_name in ["cortex_train.jsonl", "cortex_v2_train.jsonl"]:
    p = Path(__file__).resolve().parent / dataset_name
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    import re
                    words = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", item["text"].lower())
                    all_words.update(words)

# Add words from Obsidian vault
vault_dir = Path(__file__).resolve().parent.parent / "obsidian_vault"
if vault_dir.exists():
    for root, _, files in os.walk(vault_dir):
        for f in files:
            if f.endswith(".md"):
                content = open(Path(root) / f, "r", encoding="utf-8", errors="ignore").read()
                words = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", content.lower())
                all_words.update(words)

print(f"Total Unique Lexicon Words Gathered: {len(all_words)}")

out_path = Path(__file__).resolve().parent / "seed_lexicon.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(sorted(list(all_words)), f, indent=2)

print(f"Saved seed lexicon to {out_path}")
