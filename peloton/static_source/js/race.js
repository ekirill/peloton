const Directions = Object.freeze({
    CW:   "cw",
    CCW:  "ccw",
});

class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

class TrackPosition extends Point {
    constructor(x, y, degree) {
        super(x,y);
        this.degree = degree;
    }
}

function rads(degree) {
    return degree * (Math.PI / 180.0);
}

function translatePoint(p, degree, length) {
    const
        rad = rads(degree % 360),
        dx = length * Math.cos(rad),
        dy = length * Math.sin(rad),
        newX = p.x + dx,
        newY = p.y + dy;
    return new Point(newX, newY);
}

class Sector {
    constructor(sector_id, startPosition, length, radius, direction, distanceFromStart) {
        this.sector_id = sector_id;
        this.startPosition = startPosition;
        this.length = length;
        this.radius = radius;
        this.direction = direction;
        this.distanceFromStart = distanceFromStart;
        this.isCurve = this.radius !== null;

        if (this.isCurve)  {
            this.setCurveData();
        } else {
            this.setLineData();
        }
    }

    setCurveData() {
        let
            arcC, arcStartDegree, arcEndDegree, degreeN, turnDegree, isCCW,
            endPoint, endDegree;

        degreeN = this.startPosition.degree % 360;
        turnDegree = (180 * this.length) / (Math.PI * this.radius);

        if (this.direction === Directions.CW) {
            arcStartDegree = degreeN - 90;
            arcEndDegree = arcStartDegree + turnDegree;
            arcC = translatePoint(this.startPosition, degreeN + 90, this.radius);
            this.isCCW = false;
        } else {
            arcStartDegree = degreeN + 90;
            arcEndDegree = arcStartDegree - turnDegree;
            arcC = translatePoint(this.startPosition, degreeN - 90, this.radius);
            this.isCCW = true;
        }

        arcStartDegree = arcStartDegree % 360;
        if (arcStartDegree < 0) {
            arcStartDegree = 360 + arcStartDegree;
        }
        arcEndDegree = arcEndDegree % 360;
        if (arcEndDegree < 0) {
            arcEndDegree = 360 + arcEndDegree;
        }

        this.arcCenter = arcC;
        this.arcStartDegree = arcStartDegree;
        this.arcEndDegree = arcEndDegree;

        endPoint = translatePoint(arcC, arcEndDegree, this.radius);
        if (this.direction === Directions.CW) {
            endDegree = arcEndDegree + 90;
        } else {
            endDegree = arcEndDegree - 90;
        }
        endDegree = endDegree % 360;
        if (endDegree < 0) {
            endDegree = 360 + endDegree;
        }

        this.endPosition = new TrackPosition(endPoint.x, endPoint.y, endDegree);
    }

    setLineData() {
        const
            translatedP = translatePoint(this.startPosition, this.startPosition.degree, this.length);

        this.endPosition = new TrackPosition(translatedP.x, translatedP.y, this.startPosition.degree);
    }

    boundingBox() {
        if (this.isCurve) {
            // only endpoints or compass(0, 90, 180, 270) points of the arc may touch the bounding box
            let maxX, maxY, minX, minY, angStart, angEnd;
            maxX = Math.max(this.startPosition.x, this.endPosition.x);
            maxY = Math.max(this.startPosition.y, this.endPosition.y);
            minX = Math.min(this.startPosition.x, this.endPosition.x);
            minY = Math.min(this.startPosition.y, this.endPosition.y);

            angStart = this.arcStartDegree;
            angEnd = this.arcEndDegree;
            if (this.isCCW) {
                angStart = this.arcEndDegree;
                angEnd = this.arcStartDegree;
            }

            if (angEnd < angStart) {
                angEnd = 360 + angEnd;
            }

            if ((angStart <= 0 && 0 <= angEnd) || (angStart <= 360 && 360 <= angEnd)) {
                maxX = this.arcCenter.x + this.radius;
            }
            if ((angStart <= 90 && 90 <= angEnd) || (angStart <= 360 + 90 && 360 + 90 <= angEnd)) {
                maxY = this.arcCenter.y + this.radius;
            }
            if ((angStart <= 180 && 180 <= angEnd) || (angStart <= 360 + 180 && 360 + 180 <= angEnd)) {
                minX = this.arcCenter.x - this.radius;
            }
            if ((angStart <= 270 && 270 <= angEnd) || (angStart <= 360 + 270 && 360 + 270 <= angEnd)) {
                minY = this.arcCenter.y - this.radius;
            }

            return [[minX, minY], [maxX, maxY]]
        } else {
            return [
                [
                    Math.min(this.startPosition.x, this.endPosition.x),
                    Math.min(this.startPosition.y, this.endPosition.y)
                ],
                [
                    Math.max(this.startPosition.x, this.endPosition.x),
                    Math.max(this.startPosition.y, this.endPosition.y)
                ]
            ]
        }
    }

    draw(ctx) {
        if (this.isCurve)  {
            ctx.arc(
                this.arcCenter.x, this.arcCenter.y, this.radius,
                rads(this.arcStartDegree), rads(this.arcEndDegree),
                this.isCCW
            );
        } else {
            ctx.lineTo(this.endPosition.x, this.endPosition.y);
        }
    }

    isOnSector(distanceFromStart) {
        return (
            this.distanceFromStart <= distanceFromStart
            && distanceFromStart < this.distanceFromStart + this.length
        );
    }

    getCarBounds(carPosition) {
        const
            carPoint = new Point(carPosition.x, carPosition.y),
            carDegree = carPosition.degree,
            carNose = translatePoint(carPoint, carDegree, 10),
            carRight = translatePoint(carPoint, carDegree + 135, 10),
            carLeft = translatePoint(carPoint, carDegree - 135, 10);

        return {
            nose: carNose,
            right: carRight,
            left: carLeft,
        }
    }

    undrawCar(ctx, carPosition) {
        const
            carBounds = this.getCarBounds(carPosition),
            minX = Math.min(carBounds.nose.x, carBounds.right.x, carBounds.left.x) - 1,
            minY = Math.min(carBounds.nose.y, carBounds.right.y, carBounds.left.y) - 1,
            maxX = Math.max(carBounds.nose.x, carBounds.right.x, carBounds.left.x) + 1,
            maxY = Math.max(carBounds.nose.y, carBounds.right.y, carBounds.left.y) + 1;

        ctx.clearRect(minX, minY, maxX, maxY);
    }

    drawCar(ctx, distanceFromStart, oldCarPosition) {
        const length = distanceFromStart - this.distanceFromStart;
        let carPoint, carDegree;

        if (this.isCurve)  {
            const turnDegree = (180 * length) / (Math.PI * this.radius);
            let carArcDegree;
            if (this.direction === Directions.CW) {
                carArcDegree = this.arcStartDegree + turnDegree;
            } else {
                carArcDegree = this.arcStartDegree - turnDegree;
            }
            carArcDegree = carArcDegree % 360;
            if (carArcDegree < 0) {
                carArcDegree = 360 + carArcDegree;
            }
            carPoint = translatePoint(this.arcCenter, carArcDegree, this.radius);

            if (this.direction === Directions.CW) {
                carDegree = carArcDegree + 90;
            } else {
                carDegree = carArcDegree - 90;
            }
            carDegree = carDegree % 360;
            if (carDegree < 0) {
                carDegree = 360 + carDegree;
            }
        } else {
            carPoint = translatePoint(
                this.startPosition, this.startPosition.degree, length
            );
            carDegree = this.startPosition.degree;
        }

        const
            carPosition = new TrackPosition(carPoint.x, carPoint.y, carDegree),
            carBounds = this.getCarBounds(carPosition);

        if (oldCarPosition) {
            this.undrawCar(ctx, oldCarPosition);
        }
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.moveTo(carBounds.nose.x, carBounds.nose.y);
        ctx.lineTo(carBounds.right.x, carBounds.right.y);
        ctx.lineTo(carBounds.left.x, carBounds.left.y);
        ctx.closePath();
        ctx.fill();

        return carPosition;
    }
}

class Track {
    constructor(trackId, trackName, startPosition, sectors) {
        this.trackId = trackId;
        this.trackName = trackName;
        this.sectors = [];
        this.startPosition = startPosition;
        this.length = 0.0;
        let currentPosition = startPosition,
            distanceFromStart = 0.0,
            sector;
        sectors.forEach((sectorData, idx) => {
            sector = new Sector(
                idx,
                currentPosition, sectorData.length, sectorData.curve_radius,
                sectorData.curve_direction === "left" ? Directions.CCW : Directions.CW,
                distanceFromStart
            );
            currentPosition = sector.endPosition;
            distanceFromStart = distanceFromStart + sectorData.length;

            this.sectors.push(sector);
            this.length = this.length + sectorData.length;
        });
    }

    boundingBox() {
        let minX, minY, maxX, maxY, sectorBBox;
        this.sectors.forEach((sector) => {
            sectorBBox = sector.boundingBox();
            if (minX === undefined) {
                minX = sectorBBox[0][0];
                minY = sectorBBox[0][1];
                maxX = sectorBBox[1][0];
                maxY = sectorBBox[1][1];
            } else {
                minX = Math.min(minX, sectorBBox[0][0]);
                minY = Math.min(minY, sectorBBox[0][1]);
                maxX = Math.max(maxX, sectorBBox[1][0]);
                maxY = Math.max(maxY, sectorBBox[1][1]);
            }
        });
        return [[minX, minY], [maxX, maxY]];
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.moveTo(this.startPosition.x, this.startPosition.y);

        this.sectors.forEach((sector) => {
            sector.draw(ctx);
        });

        ctx.lineWidth = 3;
        ctx.strokeStyle = "blue";
        ctx.stroke();

        const
            trackBBox = this.boundingBox(),
            nameX = trackBBox[0][0],
            nameY = trackBBox[0][1] - 5;

        ctx.font = "14px Arial";
        ctx.fillStyle = "black";
        ctx.fillText(this.trackName, nameX, nameY);
    }

    getSector(distanceFromStart) {
        for (let sector of this.sectors) {
            if (sector.isOnSector(distanceFromStart)) {
                return sector;
            }
        }
        if (this.sectors.length > 0) {
            return this.sectors[this.sectors.length - 1];
        }
    }

    drawCar(ctx, distanceFromStart, oldCarPosition) {
        distanceFromStart = distanceFromStart % this.length;
        let sector = this.getSector(distanceFromStart);
        if (!sector) {
            return;
        }

        return sector.drawCar(ctx, distanceFromStart, oldCarPosition);
    }
}

class Race {
    constructor(track) {
        this.track = track;
    }

    run() {
        let dictanceFromStart = 0.0,
            oldCarPosition;

        const race = this;

        function rideCar(dictanceFromStart) {
            oldCarPosition = race.track.drawCar(ctx_layer_2, dictanceFromStart, oldCarPosition);

            setTimeout(
                function() {
                    rideCar(dictanceFromStart + 2);
                },
                10
            );
        }
        rideCar(dictanceFromStart);
    }
}
