import json
import argparse
import os
import os.path as osp
import logging
import pandas as pd

TEMPLATE_PATH = 'generation-data/chrombpnet/chrombpnet-washu-template.json'
CHROMBPNET_PATH = '/oak/stanford/groups/akundaje/projects/chromatin-atlas-2022/bigwigs'
LOG_PATH = 'logs/chrombpnet-log.txt'
atac_metadata = pd.read_csv('generation-data/encode-reports/atac_metadata.tsv', sep="\t",skiprows=1)
dnase_metadata = pd.read_csv('generation-data/encode-reports/dnase_metadata.tsv', sep="\t",skiprows=1)
# Global context
args = None

if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename=LOG_PATH, filemode='w', format='%(levelname)s: %(message)s\n\n', level=logging.INFO)

print(f"Logging to {LOG_PATH}")

def check_files_exist(exp_id, files, mode):
    dir = osp.join(CHROMBPNET_PATH,
                   mode,
                   exp_id,
                   )
    # TODO: remove when ATAC fold 0 tracks are available
    subdir = lambda file: 'chrombpnet_model_feb15_fold_1' if \
        mode == 'ATAC' and file != f"{exp_id}.bigWig" else ''
    file_paths = [osp.join(dir, subdir(file), file) for file in files]
    files_exist = [osp.isfile(file) for file in file_paths]
    all_files_exist = all(files_exist)
    if not all_files_exist:
        logging.warning(f"Files missing for experiment {exp_id}: {[file for file, exists in zip(file_paths, files_exist) if not exists]}")
    return all_files_exist
    

def construct_exp_tracks(exp_id, mode):
    with open(TEMPLATE_PATH) as f:
        template = f.read()
    # Fill in template prior to parsing
    template = template.replace('$experiment', exp_id)
    template = template.replace('$mode', mode)
    tracks = json.loads(template)
    
    # TODO: remove when CCRE tracks are available
    tracks = [track for track in tracks if 'ccre' not in track['name']]
    
    # Add metadata
    metadata_src = atac_metadata if mode == 'ATAC' else dnase_metadata 
    metadata_row = metadata_src[metadata_src['Accession'] == exp_id].reset_index()
    if (len(metadata_row) != 1):
        # print(exp_id)
        # print(metadata_row)
        logging.warning(f"Experiment {exp_id} does not have only one entry in metadata. Instead, {len(metadata_row)} entries were found.")
        return
    for track in tracks:
        # TODO: remove when ATAC fold 0 tracks are available
        if 'observed' not in track['name'] and mode == 'ATAC':
            track['url'] = track['url'].replace(exp_id, f"{exp_id}/chrombpnet_model_feb15_fold_1", 1)
        track['metadata']['biosample summary'] = metadata_row.at[0, 'Biosample summary']
        track['metadata']['biosample term name'] = metadata_row.at[0, 'Biosample term name']
        track['metadata']['life stage'] = metadata_row.at[0, 'Life stage']
    template_files = [osp.basename(track['url']) for track in tracks]
    files_exist = check_files_exist(exp_id, template_files, mode)
    if files_exist:
        return tracks
    

def construct_hub(exp_ids, mode):
    hub_tracks = []
    skipped = 0
    for exp in exp_ids:
        res = construct_exp_tracks(exp, mode)
        if res:
            hub_tracks.extend(res)
        else:
            skipped += 1
    logging.info(f"{mode} tracks completed. Skipped {skipped} experiments total")
    return hub_tracks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fills in the ChromBPNet WashU browser template')
    parser.add_argument('-a', '--atac', help='A file containing the ATAC experiment IDs', required=True)
    parser.add_argument('-d', '--dnase', help='A file containing the DNASE experiment IDs', required=True)
    parser.add_argument('-o', '--output', help='Output hub file', required=True)
    args = parser.parse_args()
    
    with open(args.atac) as f:
        atac_ids = f.read().splitlines()
    with open(args.dnase) as f:
        dnase_ids = f.read().splitlines()
    
    with open(args.output, 'w') as f:
        tracks = construct_hub(atac_ids, 'ATAC') + construct_hub(dnase_ids, 'DNASE')
        json.dump(tracks, f, indent=2)
    

