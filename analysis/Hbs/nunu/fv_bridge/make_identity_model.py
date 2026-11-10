import tensorflow as tf

x = tf.keras.Input(shape=(8,), name="features")
tf.keras.Model(x, tf.keras.layers.Activation("linear")(x)).save("identity8.keras")
