# Create Grid-Data-Model's Distribution System

A GitHub action to create [Grid-Data-Model's](https://github.com/NREL-Distribution-Suites/grid-data-models) Distribution System json files in your repository.

This repository is also being used to store raw files/dataset necessary to create Distribution System json files. This action is designed to be used in conjunction with other steps to create pull request (PR) to your repository. 

`gdm-case-action` will:

* Read all the `Master.dss` files by iterating through all folders located in `opendss` directory and converts into `DistributionSystem` json files and dumps into user speficied repository directory.

## Usage

```yml

    - uses: actions/checkout@v4

    # Create GDM's DistributionSystem json files here

    - name: Create GDM's DistributionSystem json files
      uses: NREL-Distribution-Suites/gdm-case-action@
      id: case_builder
      with:
        datapath: data
    
    # Create PR

    - name: peter-evans/create-pull-request@v7
      if: ${{steps.case_builder.outputs.branch}}
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        branch: ${{ steps.case_builder.outputs.branch }}
        title: ${{ steps.case_builder.outputs.branch }}
        commit-message: ${{ steps.case_builder.outputs.branch }}
        add-paths: |
            data/**
        base: main
        body: 'This pull request was automatically created.'
```

## Action outputs

The following outputs can be used by subsequent workflow steps.

* `branch`: Name of the branch you can use to create pull request.

## Datasets

| Name | Contributor | Description |
|------|------------|--------------|
| `p5r` | [@KapilDuwadi](https://github.com/KapilDuwadi) |  Slightly modified version of sub feeder within `P5R` region SMARTDS data from `SFO` area. Added PVsystem.|
| `testcasev1` | [@KapilDuwadi](https://github.com/KapilDuwadi) |  Simple test case for CADET testing.|
| `three_feeder_switch` | [@abodh](https://github.com/abodh) | Three feeder test case with switches.|

## Adding New Dataset

If you want to add new OpenDSS dataset for automatic GDM system creation, please add a folder inside `opendss` folder at the root of this repo by checking out a new branch. Make sure that entry file is named `Master.dss`. Add `doc.json` in the same folder, make sure to comply with `distribution_system.json` schema. Submit a pull request. 