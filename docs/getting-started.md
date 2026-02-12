---
title: Getting Started
nav_order: 2
---

The dataset must be opened through SpineToolbox (from v0.11.0, [SpineToolbox](https://github.com/spine-tools/Spine-Toolbox)). Spine Toolbox is an open source Python package to manage data, scenarios and workflows for modelling and simulation. You can have your local workflow, but work as a team through version control and SQL databases.

The main folder contains and configurable file (userconfig.yml) to develop the target model. In principle, running INES builder tool, the user will get the whole Pan-European model at country resolution for onshore and seabasin-country resolution for offshore. The target model is formatted through an interoperable energy system data specification [INES](https://github.com/ines-tools/ines-spec).

# Use This Dataset

Run SpineToolbox and open the dataset spine project ("file" tab). To do that, choose the folder that contains ".spinetoolbox" folder and the other ones.

![ProjectFolder](figs/project_folder.png)

![OpenProject](figs/open_a_project_spinetoolbox.png)

Each pipeline imports the raw to an intermediate sqlite database. Then, each one feeds a tool that creates the target model at the target resolution based on an user configuration file in the data_pipelines/europe/ folder.
