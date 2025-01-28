from skimage.filters import gaussian
import numpy as np
import pandas as pd
from PIL import Image
import json
import os
import argparse
from tqdm import tqdm


def expanded_mask(path, tsfm, canvas_size=(10000, 10000), sig=16):
    image = Image.open(path).convert('RGBA').resize((2000, 2000)).rotate(tsfm['rot'], expand=True)
    canvas = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    height, width = image.size
    x, y = tsfm['offset']
    x, y = np.round(x).astype(int) - (height // 2) + 2500, np.round(y).astype(int) - (width // 2) + 2500
    canvas.paste(image, (x, y), image)
    mask = np.array(canvas)[:, :, 3]
    mask = gaussian(mask, sig)
    return mask > 0


def handle_missing(frag_paths, tsfms, name):
    if len(frag_paths) > len(tsfms):
        print(f"Missing transformations in {name} for {len(frag_paths) - len(tsfms)} fragments, ignoring untransformed fragments")
        relevant_rpfs = [tsfm['rpf'] for tsfm in tsfms]
        for frag_path in frag_paths:
            rpf = 'RPf_' + frag_path.split('_')[1]
            if rpf not in relevant_rpfs:
                frag_paths.remove(frag_path)
    elif len(frag_paths) < len(tsfms):
        print(f"Missing fragments in {name} for {len(tsfms) - len(frag_paths)} transformations, ignoring untransformed fragments")
        relevant_rpfs = ['RPf' + frag_path.split('_')[1] for frag_path in frag_paths]
        for tsfm in tsfms:
            if tsfm['rpf'] not in relevant_rpfs:
                tsfms.remove(tsfm)
    if len(frag_paths) != len(tsfms):
        frag_paths, tsfms = handle_missing(frag_paths, tsfms, name)
    return frag_paths, tsfms


def calc_adj_matrix(frag_paths, tsfm_path, csv_path='adj.csv', json_path='adj.json'):  
    
    frag_paths.sort(key=lambda x: x.split('_')[1])
    tsfms = [
        {
            'rpf': tsfm['rpf'],
            'offset': (tsfm['x'], tsfm['y']),
            'rot': tsfm['rot'],
        }
    for tsfm in pd.read_csv(tsfm_path).to_dict(orient='records')]
    tsfms.sort(key=lambda x: x['rpf'])

    if len(frag_paths) != len(tsfms):
        frag_paths, tsfms = handle_missing(frag_paths, tsfms, name=tsfm_path.split('\\')[-1])

    masks = [expanded_mask(frag, tsfm) for frag, tsfm in zip(frag_paths, tsfms)]
    n_frags = len(masks)
    
    adj = np.zeros((n_frags, n_frags))
    for i in range(n_frags):
        for j in range(i + 1, n_frags):
            if np.sum(np.logical_and(masks[i], masks[j])) > 0:
                adj[i, j] = adj[j, i] = 1

    frag_names = ["RPf_" + path.split('\\')[-1].split('_')[1] for path in frag_paths]
    if csv_path is not None:
        adj_df = pd.DataFrame(adj, columns=frag_names)
        adj_df.to_csv(csv_path, index=False)

    if json_path is not None:
        adj_dict = {}
        for i, frag in enumerate(frag_names):
            adj_dict[frag] = [frag_names[j] for j in range(n_frags) if adj[i, j] == 1]
        with open(json_path, 'w') as f:
            json.dump(adj_dict, f, indent=4)

    return adj


def dir_to_frag_paths(dir_path):
    return [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.png')]


def process_batch(frag_dirs_root, tsfm_dir, out_dir):
    for frag_dir in tqdm(os.listdir(frag_dirs_root)):
        frag_paths = dir_to_frag_paths(os.path.join(frag_dirs_root, frag_dir))
        tsfm_path = os.path.join(tsfm_dir, frag_dir + '.csv')
        csv_path = os.path.join(out_dir, frag_dir + '.csv')
        json_path = os.path.join(out_dir, frag_dir + '.json')
        if not os.path.exists(tsfm_path):
            print(f"Transformaiton file {tsfm_path} not found, skipping this directory")
            continue
        if os.path.exists(csv_path) and os.path.exists(json_path):
            continue
        tqdm.write(frag_dir)
        calc_adj_matrix(frag_paths, tsfm_path, csv_path, json_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate adjacency matrix')
    parser.add_argument('frag_dir', type=str, help='Directory containing puzzle fragments (each in a separate sub-directory)')
    parser.add_argument('tsfm_dir', type=str, help='Path to transformations directory in CSV format')
    parser.add_argument('out_dir', type=str, help='Output directory for adjacency matrices')

    args = parser.parse_args()

    process_batch(args.frag_dir, args.tsfm_dir, args.out_dir)

