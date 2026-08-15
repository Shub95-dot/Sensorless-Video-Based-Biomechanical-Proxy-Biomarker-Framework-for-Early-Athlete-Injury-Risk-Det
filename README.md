# Sensorless Video‑Based Biomechanical Proxy Biomarker Framework for Early Athlete Injury Risk Detection

Short description
-----------------
An open-source framework for sensorless 3D biomechanics and multimodal athlete workload analysis that uses standard RGB video and deep learning to (1) estimate 3D pose and joint loading proxies from monocular video, (2) compute longitudinal workload and biomechanical proxy biomarkers, and (3) predict early injury risk without wearable hardware. The codebase provides preprocessing, model training and inference, evaluation suites, and reproducible experiment recipes intended for publication-level release and reuse.

Abstract
--------
This repository implements the methods described in the associated manuscript for sensorless, video-based estimation of biomechanical proxies and subsequent injury-risk modeling. Our framework combines state-of-the-art 2D/3D pose estimation, physics‑informed proxy derivations, temporal workload modeling, and supervised risk prediction. It is designed for reproducible research: packaged environment recipes, experiment manifests, evaluation metrics, and example datasets are included to facilitate replication and comparison.

Highlights
----------
- Monocular RGB-to-3D pose pipeline optimized for athlete motion.
- Biomechanical proxy computations (joint angles, angular velocities, proxy load metrics) derived without force-plate or wearables.
- Temporal workload aggregation and risk classification/regression modules.
- End-to-end reproducible experiments and evaluation scripts.
- Designed for deployment on consumer video (standard frame rates and resolutions).

Table of contents
-----------------
- Abstract
- Installation & Requirements
- Quick start (inference, evaluation, training)
- Pipeline & methods overview
- Data: format and organization
- Reproducibility and experiment recipes
- Evaluation protocol and metrics
- Limitations and ethical considerations
- Citation & References
- License and acknowledgments
- Contact

Installation & requirements
---------------------------
Prerequisites
- Python 3.8 or later (3.9+ recommended)
- CUDA 11.x + cuDNN (for GPU acceleration), or CPU-only for small-scale inference
- Git, Make (optional), and ffmpeg (for video preprocessing)

Recommended environment (conda)
1. Create environment
   conda create -n svbbf python=3.9
   conda activate svbbf

2. Install dependencies
   pip install -r requirements.txt

Notes
- If a requirements file is not present, install core packages: torch (version matching your CUDA), torchvision, numpy, opencv-python, scikit-learn, pandas, tqdm, matplotlib, and your selected 2D pose estimator (OpenPose / HRNet / Mediapipe) bindings.
- For consistent results, use the provided environment.yml or Dockerfile if present. We recommend using the Docker recipe (if included) for reproducible, publication-grade runs.

Quick start
-----------
1) Prepare video(s)
- Place raw videos in a folder structured as:
  data/videos/{subject_id}/{session_id}/*.mp4

2) Run preprocessing (frame extraction, optional tracking)
- Example:
  python scripts/preprocess.py --input data/videos --output data/preprocessed --fps 30

3) Run 2D pose estimation
- Example (HRNet/OpenPose/MediaPipe):
  python scripts/pose2d.py --input data/preprocessed --out data/pose2d --model hrnet

4) Monocular 3D lifting and biomechanical proxies
- Example:
  python scripts/lift_and_compute_proxies.py --pose2d data/pose2d --out data/proxies --subject-info metadata/subjects.csv

5) Inference: injury-risk prediction
- Example:
  python scripts/infer_risk.py --proxies data/proxies --model checkpoints/risk_model.pt --out results/predictions.csv

6) Evaluation
- Example:
  python scripts/evaluate.py --pred results/predictions.csv --gt data/labels.csv --metrics auc precision_recall

Pipeline & methods overview
---------------------------
The framework implements a modular pipeline with the following components:

1. Video preprocessing
   - Frame extraction, stabilization (optional), subject cropping, and temporal segmentation.

2. 2D pose estimation
   - Off-the-shelf or custom-trained 2D keypoint detectors (configurable backbones).

3. Monocular 3D pose lifting
   - Temporal lifting network that regresses 3D joint coordinates from 2D keypoints plus temporal context.

4. Biomechanical proxy computation
   - Kinematic-derived quantities (joint angles, angular velocities, joint-segment orientations).
   - Proxy loading measures (e.g., normalized angular impulse, integrated joint rotational power proxies). These proxies are designed to serve as substitutes for instrumented measurements where wearables or force plates are unavailable.

5. Temporal workload aggregation
   - Session-level and longitudinal aggregation (rolling windows, cumulative load metrics, acute:chronic workload ratio variants).

6. Risk modeling
   - Supervised classifiers/regressors trained on proxy features and metadata to predict short-to-mid-term injury risk. Models in the repo include logistic regression, gradient-boosted trees, and temporal deep networks (LSTM/Transformer) depending on experimental configuration.

Data: format and organization
-----------------------------
Expected repository data layout (examples)
- data/
  - videos/                # raw mp4 files organized by subject/session
  - preprocessed/          # preprocessed frames / crops
  - pose2d/                # 2D keypoints (.npy or .json per video)
  - proxies/               # computed proxy features (.csv or .npz per session)
  - labels/                # ground-truth injury labels and metadata (CSV)
  - manifests/             # experiment manifests and train/val/test splits

Data format
- 2D keypoints: per-frame arrays of shape (T, J, 2) + confidence scores
- 3D keypoints: per-frame arrays of shape (T, J, 3)
- Proxy features: tabular per session with time-series or aggregated statistics
- Labels: tabular file containing subject_id, session_id, outcome (binary/continuous), and metadata columns (age, sex, sport, exposure hours)

If using protected or proprietary datasets please follow data-use agreements and remove identifying information prior to sharing.

Reproducibility and experiment recipes
-------------------------------------
- Each experiment folder includes:
  - experiment.yaml (configuration: model, hyperparameters, random seed, dataset splits)
  - requirements.txt / environment.yml
  - run.sh or Makefile with exact commands used to reproduce training and evaluation

Reproducibility guidelines:
- Fix random seeds for numpy, torch, and other RNGs (example seed: 42).
- Log hardware and software versions (Python, PyTorch, CUDA).
- Use the provided Dockerfile where absolute reproducibility is required.
- Save model checkpoints, training logs, and evaluation artifacts for auditability.

Evaluation protocol and metrics
-------------------------------
Suggested metrics:
- Classification: ROC-AUC, PR-AUC, accuracy, F1-score, sensitivity, specificity
- Regression (continuous risk scores or proxy estimates): MAE, RMSE, R^2
- Time-to-event: concordance index (if survival analysis applied)

Protocol recommendations:
- Use subject-wise splits: train/validation/test must be disjoint at subject level.
- Report mean ± standard deviation across k-fold or repeated-split experiments.
- When possible, provide external validation on independent cohorts.

Limitations and ethical considerations
--------------------------------------
- Proxy measures are not substitutes for laboratory-grade force or EMG recordings; they are intended as approximate biomarkers when instrumented data are unavailable.
- Measurement error can increase for occluded or low-resolution video — results should be interpreted with caution.
- Ensure compliance with privacy laws and ethical approvals when using video of human subjects. Anonymize or obtain consent as required.
- Avoid overreliance on automated risk scores for individual clinical decision-making without expert oversight.

How to cite
-----------
If you use this code and the associated methods, please cite the associated manuscript(s) and relevant prior work. A machine-readable bibliography is included below and can be used directly. Example repository citation (if no manuscript is available yet):

- Repository: Shub95-dot/Sensorless-Video-Based-Biomechanical-Proxy-Biomarker-Framework-for-Early-Athlete-Injury-Risk-Det
- URL: https://github.com/Shub95-dot/Sensorless-Video-Based-Biomechanical-Proxy-Biomarker-Framework-for-Early-Athlete-Injury-Risk-Det

References (BibTeX export)
-------------------------
Below is the complete BibTeX export (as provided). You may copy this into Exported Items.bib or include it in your manuscript:

```bibtex
@article{martin_bland_statistical_1986,
	title = {{STATISTICAL} {METHODS} {FOR} {ASSESSING} {AGREEMENT} {BETWEEN} {TWO} {METHODS} {OF} {CLINICAL} {MEASUREMENT}},
	volume = {327},
	copyright = {https://www.elsevier.com/tdm/userlicense/1.0/},
	issn = {01406736},
	url = {https://linkinghub.elsevier.com/retrieve/pii/S0140673686908378},
	doi = {10.1016/S0140-6736(86)90837-8},
	language = {en},
	number = {8476},
	urldate = {2026-07-27},
	journal = {The Lancet},
	author = {Martin Bland, J. and Altman, DouglasG.},
	month = feb,
	year = {1986},
	keywords = {Agreement Analysis, Bland-Altman, Methodology, Statistics, Validation},
	pages = {307--310},
}

@book{cohen_statistical_1988,
	address = {New York, NY},
	edition = {2. ed., reprint},
	title = {Statistical power analysis for the behavioral sciences},
	isbn = {978-0-8058-0283-2},
	language = {eng},
	publisher = {Psychology Press},
	author = {Cohen, Jacob},
	year = {1988},
	note = {Original Date: 1988},
	annote = {Literaturverz. S. 553 - 558},
	file = {Table of Contents PDF:C\\:\\Users\\shiro\\Zotero\\storage\\4XF4AUX9\\Cohen - 1988 - Statistical power analysis for the behavioral sciences.pdf:application/pdf},
}

@article{savitzky_smoothing_1964,
	title = {Smoothing and {Differentiation} of {Data} by {Simplified} {Least} {Squares} {Procedures}.},
	volume = {36},
	issn = {0003-2700, 1520-6882},
	url = {https://pubs.acs.org/doi/abs/10.1021/ac60214a047},
	doi = {10.1021/ac60214a047},
	language = {en},
	number = {8},
	urldate = {2026-07-27},
	journal = {Analytical Chemistry},
	author = {Savitzky, Abraham. and Golay, M. J. E.},
	month = jul,
	year = {1964},
	pages = {1627--1639},
}

@article{bahr_why_2016,
	title = {Why screening tests to predict injury do not work—and probably never will…: a critical review},
	volume = {50},
	issn = {0306-3674, 1473-0480},
	shorttitle = {Why screening tests to predict injury do not work—and probably never will…},
	url = {https://bjsm.bmj.com/lookup/doi/10.1136/bjsports-2016-096256},
	doi = {10.1136/bjsports-2016-096256},
	abstract = {This paper addresses if and how a periodic health examination to screen for risk factors for injury can be used to mitigate injury risk. The key question asked is whether it is possible to use screening tests to identify who is at risk for a sports injury—in order to address the deficit through a targeted intervention programme. The paper demonstrates that to validate a screening test to predict and prevent sports injuries, at least 3 steps are needed. First, a strong relationship needs to be demonstrated in prospective studies between a marker from a screening test and injury risk (step 1). Second, the test properties need to be examined in relevant populations, using appropriate statistical tools (step 2). Unfortunately, there is currently no example of a screening test for sports injuries with adequate test properties. Given the nature of potential screening tests (where test performance is usually measured on a continuous scale from low to high), substantial overlap is to be expected between players with high and low risk of injury. Therefore, although there are a number of tests demonstrating a statistically significant association with injury risk, and therefore help the understanding of causative factors, such tests are unlikely to be able to predict injury with sufficient accuracy. The final step needed is to document that an intervention programme targeting athletes identified as being at high risk through a screening programme is more beneficial than the same intervention programme given to all athletes (step 3). To date, there is no intervention study providing support for screening for injury risk.},
	language = {en},
	number = {13},
	urldate = {2026-07-27},
	journal = {British Journal of Sports Medicine},
	author = {Bahr, Roald},
	month = jul,
	year = {2016},
	pages = {776--780},
	file = {Full Text:C\\:\\Users\\shiro\\Zotero\\storage\\FJHUHJUR\\Bahr - 2016 - Why screening tests to predict injury do not work—and probably never will… a critical review.pdf:application/pdf},
}

@article{colyer_review_2018,
	title = {A {Review} of the {Evolution} of {Vision}-{Based} {Motion} {Analysis} and the {Integration} of {Advanced} {Computer} {Vision} {Methods} {Towards} {Developing} a {Markerless} {System}},
	volume = {4},
	issn = {2199-1170, 2198-9761},
	url = {https://sportsmedicine-open.springeropen.com/articles/10.1186/s40798-018-0139-y},
	doi = {10.1186/s40798-018-0139-y},
	language = {en},
	number = {1},
	urldate = {2026-07-27},
	journal = {Sports Medicine - Open},
	author = {Colyer, Steffi L. and Evans, Murray and Cosker, Darren P. and Salo, Aki I. T.},
	month = dec,
	year = {2018},
	pages = {24},
	file = {Full Text PDF:C\\:\\Users\\shiro\\Zotero\\storage\\QKG5I9H5\\Colyer et al. - 2018 - A Review of the Evolution of Vision-Based Motion Analysis and the Integration of Advanced Computer V.pdf:application/pdf},
}

@article{halilaj_machine_2018,
	title = {Machine learning in human movement biomechanics: {Best} practices, common pitfalls, and new opportunities},
	volume = {81},
	issn = {00219290},
	shorttitle = {Machine learning in human movement biomechanics},
	url = {https://linkinghub.elsevier.com/retrieve/pii/S0021929018307309},
	doi = {10.1016/j.jbiomech.2018.09.009},
	language = {en},
	urldate = {2026-07-27},
	journal = {Journal of Biomechanics},
	author = {Halilaj, Eni and Rajagopal, Apoorva and Fiterau, Madalina and Hicks, Jennifer L. and Hastie, Trevor J. and Delp, Scott L.},
	month = nov,
	year = {2018},
	pages = {1--11},
}

@misc{lugaresi_mediapipe_2019,
	title = {{MediaPipe}: {A} {Framework} for {Building} {Perception} {Pipelines}},
	shorttitle = {{MediaPipe}},
	url = {http://arxiv.org/abs/1906.08172},
	doi = {10.48550/arXiv.1906.08172},
	abstract = {Building applications that perceive the world around them is challenging. A developer needs to (a) select and develop corresponding machine learning algorithms and models, (b) build a series of prototypes and demos, (c) balance resource consumption against the quality of the solutions, and finally (d) identify and mitigate problematic cases. The MediaPipe framework addresses all of these challenges. A developer can use MediaPipe to build prototypes by combining existing perception components, to advance them to polished cross-platform applications and measure system performance and resource consumption on target platforms. We show that these features enable a developer to focus on the algorithm or model development and use MediaPipe as an environment for iteratively improving their application with results reproducible across different devices and platforms. MediaPipe will be open-sourced at https://github.com/google/mediapipe.},
	urldate = {2026-07-27},
	publisher = {arXiv},
	author = {Lugaresi, Camillo and Tang, Jiuqiang and Nash, Hadon and McClanahan, Chris and Uboweja, Esha and Hays, Michael and Zhang, Fan and Chang, Chuo-Ling and Yong, Ming Guang and Lee, Juhyun and Chang, Wan-Teh and Hua, Wei and Georg, Manfred and Grundmann, Matthias},
	month = jun,
	year = {2019},
	note = {arXiv:1906.08172 [cs.DC]},
	keywords = {Computer Science - Distributed, Parallel, and Cluster Computing},
	file = {Preprint PDF:C\\:\\Users\\shiro\\Zotero\\storage\\M4BK5C5E\\Lugaresi et al. - 2019 - MediaPipe A Framework for Building Perception Pipelines.pdf:application/pdf},
}

@inproceedings{mundt_m_prediction_2019,
	title = {Prediction of joint kinetics based on joint kinematics using artificial neural networks},
	booktitle = {{ISBS} {Proceedings}},
	author = {{Mundt, M.} and {Koeppe, A.} and {David, S.} and {Bamer, F.} and {Potthast, W.} and {Markert, B.}},
	year = {2019},
}

@inproceedings{mundt_prediction_2018,
	title = {Prediction of joint kinetics based on joint kinematics using neural networks},
	url = {https://sprinz.aut.ac.nz/__data/assets/pdf_file/0012/203106/227_1319_Mundt.pdf},
	urldate = {2026-07-27},
	booktitle = {Proceedings of the 36th {Conference} of the {International} {Society} of {Biomechanics} in {Sports}, {Auckland}, {New} {Zealand}},
	author = {Mundt, Marion and Koeppe, Arnd and Bamer, Franz and Potthast, Wolfgang and Markert, Bernd},
	year = {2018},
	pages = {10--14},
	file = {Available Version (via Google Scholar):C\\:\\Users\\shiro\\Zotero\\storage\\MQRHB35B\\Mundt et al. - 2018 - Prediction of joint kinetics based on joint kinematics using neural networks.pdf:application/pdf},
}

@article{wade_applications_2022,
	title = {Applications and limitations of current markerless motion capture methods for clinical gait biomechanics},
	volume = {10},
	copyright = {https://creativecommons.org/licenses/by/4.0/},
	issn = {2167-8359},
	url = {https://peerj.com/articles/12995},
	doi = {10.7717/peerj.12995},
	abstract = {Background
              Markerless motion capture has the potential to perform movement analysis with reduced data collection and processing time compared to marker-based methods. This technology is now starting to be applied for clinical and rehabilitation applications and therefore it is crucial that users of these systems understand both their potential and limitations. The literature review aims to provide a comprehensive overview of the current state of markerless motion capture for both single camera and multi-camera systems. Additionally, this review explores how practical applications of markerless technology are being used in clinical and rehabilitation settings, and examines the future challenges and directions markerless research must explore to facilitate full integration of this technology within clinical biomechanics.
            
            
              Methodology
              A scoping review is needed to examine this emerging broad body of literature and determine where gaps in knowledge exist, this is key to developing motion capture methods that are cost effective and practically relevant to clinicians, coaches and researchers around the world. Literature searches were performed to examine studies that report accuracy of markerless motion capture methods, explore current practical applications of markerless motion capture methods in clinical biomechanics and identify gaps in our knowledge that are relevant to future developments in this area.
            
            
              Results
              Markerless methods increase motion capture data versatility, enabling datasets to be re-analyzed using updated pose estimation algorithms and may even provide clinicians with the capability to collect data while patients are wearing normal clothing. While markerless temporospatial measures generally appear to be equivalent to marker-based motion capture, joint center locations and joint angles are not yet sufficiently accurate for clinical applications. Pose estimation algorithms are approaching similar error rates of marker-based motion capture, however, without comparison to a gold standard, such as bi-planar videoradiography, the true accuracy of markerless systems remains unknown.
            
            
              Conclusions
              Current open-source pose estimation algorithms were never designed for biomechanical applications, therefore, datasets on which they have been trained are inconsistently and inaccurately labelled. Improvements to labelling of open-source training data, as well as assessment of markerless accuracy against gold standard methods will be vital next steps in the development of this technology.},
	language = {en},
	urldate = {2026-07-27},
	journal = {PeerJ},
	author = {Wade, Logan and Needham, Laurie and McGuigan, Polly and Bilzon, James},
	month = feb,
	year = {2022},
	pages = {e12995},
	file = {Full Text PDF:C\\:\\Users\\shiro\\Zotero\\storage\\FUYQX5J6\\Wade et al. - 2022 - Applications and limitations of current markerless motion capture methods for clinical gait biomecha.pdf:application/pdf},
}

@article{uhlrich_opencap_2023,
	title = {{OpenCap}: {Human} movement dynamics from smartphone videos},
	volume = {19},
	issn = {1553-7358},
	shorttitle = {{OpenCap}},
	url = {https://dx.plos.org/10.1371/journal.pcbi.1011462},
	doi = {10.1371/journal.pcbi.1011462},
	abstract = {Measures of human movement dynamics can predict outcomes like injury risk or musculoskeletal disease progression. However, these measures are rarely quantified in large-scale research studies or clinical practice due to the prohibitive cost, time, and expertise required. Here we present and validate OpenCap, an open-source platform for computing both the kinematics (i.e., motion) and dynamics (i.e., forces) of human movement using videos captured from two or more smartphones. OpenCap leverages pose estimation algorithms to identify body landmarks from videos; deep learning and biomechanical models to estimate three-dimensional kinematics; and physics-based simulations to estimate muscle activations and musculoskeletal dynamics. OpenCap’s web application enables users to collect synchronous videos and visualize movement data that is automatically processed in the cloud, thereby eliminating the need for specialized hardware, software, and expertise. We show that OpenCap accurately predicts dynamic measures, like muscle activations, joint loads, and joint moments, which can be used to screen for disease risk, evaluate intervention efficacy, assess between-group movement differences, and inform rehabilitation decisions. Additionally, we demonstrate OpenCap’s practical utility through a 100-subject field study, where a clinician using OpenCap estimated musculoskeletal dynamics 25 times faster than a laboratory-based approach at less than 1\% of the cost. By democratizing access to human movement analysis, OpenCap can accelerate the incorporation of biomechanical metrics into large-scale research studies, clinical trials, and clinical practice.},
	language = {en},
	number = {10},
	urldate = {2026-07-27},
	journal = {PLOS Computational Biology},
	author = {Uhlrich, Scott D. and Falisse, Antoine and Kidziński, Łukasz and Muccini, Julie and Ko, Michael and Chaudhari, Akshay S. and Hicks, Jennifer L. and Delp, Scott L.},
	editor = {Marsden, Alison L.},
	month = oct,
	year = {2023},
	pages = {e1011462},
	file = {Full Text:C\\:\\Users\\shiro\\Zotero\\storage\\EPBAUR48\\Uhlrich et al. - 2023 - OpenCap Human movement dynamics from smartphone videos.pdf:application/pdf},
}

@inproceedings{zhang_actemes_2013,
	address = {Sydney, Australia},
	title = {From {Actemes} to {Action}: {A} {Strongly}-{Supervised} {Representation} for {Detailed} {Action} {Understanding}},
	isbn = {978-1-4799-2840-8},
	shorttitle = {From {Actemes} to {Action}},
	url = {http://ieeexplore.ieee.org/document/6751390/},
	doi = {10.1109/ICCV.2013.280},
	urldate = {2026-07-27},
	booktitle = {2013 {IEEE} {International} {Conference} on {Computer} {Vision}},
	publisher = {IEEE},
	author = {Zhang, Weiyu and Zhu, Menglong and Derpanis, Konstantinos G.},
	month = dec,
	year = {2013},
	pages = {2248--2255},
}

@article{powers_influence_2003,
	title = {The {Influence} of {Altered} {Lower}-{Extremity} {Kinematics} on {Patellofemoral} {Joint} {Dysfunction}: {A} {Theoretical} {Perspective}},
	volume = {33},
	issn = {0190-6011, 1938-1344},
	shorttitle = {The {Influence} of {Altered} {Lower}-{Extremity} {Kinematics} on {Patellofemoral} {Joint} {Dysfunction}},
	url = {http://www.jospt.org/doi/10.2519/jospt.2003.33.11.639},
	doi = {10.2519/jospt.2003.33.11.639},
	language = {en},
	number = {11},
	urldate = {2026-07-27},
	journal = {Journal of Orthopaedic \& Sports Physical Therapy},
	author = {Powers, Christopher M.},
	month = nov,
	year = {2003},
	pages = {639--646},
}

@article{farrokhi_trunk_2008,
	title = {Trunk {Position} {Influences} the {Kinematics}, {Kinetics}, and {Muscle} {Activity} of the {Lead} {Lower} {Extremity} {During} the {Forward} {Lunge} {Exercise}},
	volume = {38},
	issn = {0190-6011, 1938-1344},
	url = {http://www.jospt.org/doi/10.2519/jospt.2008.2634},
	doi = {10.2519/jospt.2008.2634},
	language = {en},
	number = {7},
	urldate = {2026-07-27},
	journal = {Journal of Orthopaedic \& Sports Physical Therapy},
	author = {Farrokhi, Shawn and Pollard, Christine D. and Souza, Richard B. and Chen, Yu-Jen and Reischl, Stephen and Powers, Christopher M.},
	month = jul,
	year = {2008},
	pages = {403--409},
}

@article{zhang_acute_2025,
	title = {Acute {Effects} of {Accelerated} {Eccentrics} and {Accentuated} {Eccentric} {Loading} on {Squat} {Performance} and {Lower}-{Limb} {Biomechanics}},
	volume = {13},
	issn = {2075-4663},
	url = {https://www.mdpi.com/2075-4663/13/12/418},
	doi = {10.3390/sports13120418},
	abstract = {This study aimed to compare the acute effects of three eccentric training strategies—constant resistance (CR), accentuated eccentric loading (AEL), and accelerated eccentrics (AE)—on the performance and biomechanical characteristics of the concentric phase of the squat, while maintaining a consistent squat depth. Twenty-four experienced resistance-trained male collegiate athletes (age: 21.92 ± 2.66 years; height: 175.88 ± 4.39 cm; body mass: 73.18 ± 8.08 kg) were recruited. A randomized crossover design was employed, where participants completed three squat protocols (eccentric load/concentric load/eccentric duration): AEL (90\% 1RM/60\% 1RM/2 s), CR (60\% 1RM/60\% 1RM/2 s), and AE (60\% 1RM/60\% 1RM/as fast as possible). Throughout the squats, kinematic and kinetic data were synchronously collected using an 8-camera 3D infrared motion capture system and two 3D force plates. The mean concentric barbell velocity in the AE condition was significantly higher than in both the AEL and CR conditions (p {\textless} 0.001). Furthermore, the AE condition demonstrated significant advantages in multiple biomechanical variables, including peak ground reaction force, as well as peak angular velocity and peak joint moments of the three lower limb joints (p {\textless} 0.05). With identical concentric loads and range of motion, increasing the velocity of the eccentric phase significantly enhances subsequent concentric performance and force output. In contrast, while the AEL strategy increases the mechanical load during the eccentric phase, its potentiating effect on concentric performance is relatively limited. These findings suggest that eccentric velocity may be a more critical variable than eccentric load in strength training.},
	number = {12},
	urldate = {2026-07-27},
	journal = {Sports},
	author = {Zhang, Mingrui and Zhou, Hao and Xiang, Xiaoyan and Wang, Ran},
	month = dec,
	year = {2025},
	pages = {418},
}

@article{wallace_patellofemoral_2002,
	title = {Patellofemoral {Joint} {Kinetics} {While} {Squatting} with and without an {External} {Load}},
	volume = {32},
	issn = {0190-6011, 1938-1344},
	url = {http://www.jospt.org/doi/10.2519/jospt.2002.32.4.141},
	doi = {10.2519/jospt.2002.32.4.141},
	language = {en},
	number = {4},
	urldate = {2026-07-27},
	journal = {Journal of Orthopaedic \& Sports Physical Therapy},
	author = {Wallace, David A. and Salem, George J. and Salinas, Ruben and Powers, Christopher M.},
	month = apr,
	year = {2002},
	pages = {141--148},
}

@article{field_bootstrapping_2007,
	title = {Bootstrapping {Clustered} {Data}},
	volume = {69},
	copyright = {https://academic.oup.com/journals/pages/open_\access/funder_policies/chorus/standard_publication_model},
	issn = {1369-7412, 1467-9868},
	url = {https://academic.oup.com/jrsssb/article/69/3/369/7109361},
	doi = {10.1111/j.1467-9868.2007.00593.x},
	abstract = {Summary
            Various bootstraps have been proposed for bootstrapping clustered data from one-way arrays. The simulation results in the literature suggest that some of these methods work quite well in practice; the theoretical results are limited and more mixed in their conclusions. For example, McCullagh reached negative conclusions about the use of non-parametric bootstraps for one-way arrays. The purpose of this paper is to extend our understanding of the issues by discussing the effect of different ways of modelling clustered data, the criteria for successful bootstraps used in the literature and extending the theory from functions of the sample mean to include functions of the between and within sums of squares and non-parametric bootstraps to include model-based bootstraps. We determine that the consistency of variance estimates for a bootstrap method depends on the choice of model with the residual bootstrap giving consistency under the transformation model whereas the cluster bootstrap gives consistent estimates under both the transformation and the random-effect model. In addition we note that the criteria based on the distribution of the bootstrap observations are not really useful in assessing consistency.},
	language = {en},
	number = {3},
	urldate = {2026-07-27},
	journal = {Journal of the Royal Statistical Society Series B: Statistical Methodology},
	author = {Field, C. A. and Welsh, A. H.},
	month = jun,
	year = {2007},
	pages = {369--390},
}

@book{borenstein_introduction_2013,
	address = {Chichester},
	edition = {Nachdr.},
	title = {Introduction to meta-analysis},
	isbn = {978-0-470-05724-7},
	language = {eng},
	publisher = {Wiley},
	editor = {Borenstein, Michael},
	year = {2013},
}

```

License
-------
See LICENSE file in this repository. If none exists, add an appropriate open-source license (e.g., MIT, Apache‑2.0) prior to public release.

Acknowledgments & funding
-------------------------
List funding sources, institutional affiliations, and acknowledgments here. Credit contributors and third-party datasets and libraries used.

Contact and support
-------------------
For issues and feature requests, please use the GitHub issues tab. For direct inquiries, contact the corresponding author at <corresponding.author@example.edu> (replace with real contact).

Contributing
------------
Contributions are welcome. Please open issues for bugs or feature requests and submit pull requests with tests and documentation updates. Include reproducible examples for any significant change.

Appendices (optional)
---------------------
- Model architectures and hyperparameters
- Detailed preprocessing and augmentation recipes
- Additional experiments and ablation studies
