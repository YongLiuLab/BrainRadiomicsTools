import json

import chainer
import chainer.functions as F
import numpy as np
from .model import VoxResNet
from .utils import load_sample, load_nifti, dice_coefficients, feedforward
import os
def validate(model, df, input_shape, output_shape, n_tiles, n_classes):
    dice_coefs = []
    for image_path, label_path in zip(df["image"], df["label"]):
        image = load_nifti(image_path)
        label = load_nifti(label_path)
        output = feedforward(
            model,
            image,
            input_shape,
            output_shape,
            n_tiles,
            n_classes)
        y = np.int32(np.argmax(output, axis=0))
        dice_coefs.append(
            dice_coefficients(y, label, labels=range(n_classes))
        )
    dice_coefs = np.array(dice_coefs)
    return np.mean(dice_coefs, axis=0)


def train(train_df,cross,validation_df=None):

    learning_rate = 1e-3
    weight_decay=0.0005
    output_shape = [60,60,60]
    input_shape = [80,80,80]
    vrn = VoxResNet(2, 4)
    iteration = 10000
    n_batch = 1
    monitor_step = 100
    n_tiles = [5,5,5]
    chainer.cuda.get_device_from_id(1).use()
    vrn.to_gpu()

    optimizer = chainer.optimizers.Adam(alpha=learning_rate)
    optimizer.use_cleargrads()
    optimizer.setup(vrn)
    optimizer.add_hook(chainer.optimizer.WeightDecay(weight_decay))
    slices_in = [slice(None), slice(None)] + [
        slice((len_in - len_out) // 2, len_in - (len_in - len_out) // 2)
        for len_out, len_in in zip(output_shape, input_shape)
    ]
    val_score=0
    if(not os.path.exists("output/cross%d" % cross)):
        os.mkdir("output/cross%d" % cross)
    dice_dict = {}
    for i in range(iteration):
        vrn.cleargrads()
        image, label = load_sample(train_df,n_batch,input_shape,output_shape)
        x_train = vrn.xp.asarray(image)
        y_train = vrn.xp.asarray(label)
        logits = vrn(x_train, train=True)
        logits = [logit[slices_in] for logit in logits]
        loss = F.softmax_cross_entropy(logits[-1], y_train)
        for logit in logits[:-1]:
            loss += F.softmax_cross_entropy(logit, y_train)
        loss.backward()
        optimizer.update()
        if i % monitor_step == 0:
            accuracy = float(F.accuracy(logits[-1], y_train).data)
            print(
                f"step {i:5d}, accuracy {accuracy:.02f}, loss {float(loss.data):g}"
            )

            if validation_df is not None:
                dice_coefs = validate(
                    vrn,
                    validation_df,
                    input_shape,
                    output_shape,
                    n_tiles,
                    4
                )
                mean_dice_coefs = np.mean(dice_coefs)
                dice_dict[i] = mean_dice_coefs
                if mean_dice_coefs >= val_score or np.abs(mean_dice_coefs - val_score)<0.1:
                    chainer.serializers.save_npz("./output/cross%d/model%d.vrn" % (cross,i), vrn)
                    print(f"step {i:5d}, saved model")
                    if mean_dice_coefs >= val_score:
                        val_score = mean_dice_coefs
                print(
                    f"step {i:5d}",
                    f"val/dice {mean_dice_coefs:.02f}",
                    *[f"val/dice{j} {dice:.02f}" for j, dice in enumerate(dice_coefs)],
                    sep=", "
                )

    if validation_df is not None:
        dice_coefs = validate(
            vrn,
            validation_df,
            input_shape,
            output_shape,
            n_tiles,
            4
        )
        mean_dice_coefs = np.mean(dice_coefs)
        if mean_dice_coefs > val_score:
            chainer.serializers.save_npz("./output/cross%d/model%d.vrn" % (cross,i), vrn)
            print(f"step {iteration:5d}, saved model")
        print(
            f"step {iteration:5d}",
            f"val/dice {mean_dice_coefs:.02f}",
            *[f"val/dice{j} {dice:.02f}" for j, dice in enumerate(dice_coefs)],
            sep=", "
        )
        dice_dict[i]=mean_dice_coefs
    else:
        chainer.serializers.save_npz("model%d.vrn" % cross, vrn)
        print(f"step {iteration:5d}, saved model")
    with open("output/cross%d/res.json" % cross,'w') as outfile:
        json.dump(dice_dict,outfile,ensure_ascii=False)
        outfile.write('\n')
    return dice_dict