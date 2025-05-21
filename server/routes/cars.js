const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Car = require('../models/Car');

// Get all cars
router.get('/', async (req, res) => {
  try {
    const cars = await Car.find().sort({ createdAt: -1 });
    res.json(cars);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Add a new car
router.post('/', auth, async (req, res) => {
  try {
    const { make, model, year, price, description, image } = req.body;
    const newCar = new Car({
      make,
      model,
      year,
      price,
      description,
      image,
      seller: req.user.id
    });
    const car = await newCar.save();
    res.json(car);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;