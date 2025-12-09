from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Penyakit, History
from fuzzy_logic import FuzzyLogic
import json