					{% if file.name1 == 'Foot' and file.name2 == 'AnteroPosterior' %}
						<!-- <div class="col-3">
							<select name="demo-category" id="demo-category">
								<option value="">Select Angle</option>
								<option value="1">HVA</option>
								<option value="1">DMAA</option>
								<option value="1">IMA</option>
								<option value="1">TaloCalcaneal Angle</option>
								<option value="1">Talonavicular Anglee</option>
								<option value="1">Incongruency Angle</option>
							</select>
						</div> -->

					</div>
					{% elif file.name1 == 'Foot' and file.name2 == 'Lateral' %}
					<div class="row gtr-uniform">
						<div class="col-2 col-12-small">
							<input type="checkbox" id="TibioCalcaneal Angle" name="TibioCalcaneal Angle">
							<label for="TibioCalcaneal Angle">TibioCalcaneal Angle</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="checkbox" id="TaloCalcaneal" name="TaloCalcaneal">
							<label for="TaloCalcaneal">TaloCalcaneal Angle</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="checkbox" id="Calcaneal Pitch" name="Calcaneal Pitch">
							<label for="Calcaneal Pitch">Calcaneal Pitch Angle</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="checkbox" id="Meary" name="Meary">
							<label for="Meary">Meary Angle</
						</div>
						<div class="col-2 col-12-small">
							<input type="checkbox" id="Gissane" name="Gissane">
							<label for="Gissane">Gissane Angle</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="checkbox" id="Böhler" name="Böhler">
							<label for="">Böhler Angle</label>
						</div>
					</div>
					{% else %}
					<div class="row gtr-uniform">
						<div class="col-2 col-12-small">
							<input type="radio" id="demo-priority-low" name="demo-priority">
							<label for="demo-priority-low">Low Priority</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="radio" id="demo-priority-normal" name="demo-priority">
							<label for="demo-priority-normal">Normal Priority</label>
						</div>
						<div class="col-2 col-12-small">
							<input type="radio" id="demo-priority-high" name="demo-priority">
							<label for="demo-priority-high">High Priority</label>
						</div>
					</div>
					{% endif %}