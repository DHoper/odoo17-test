/** @odoo-module */

import { Reactive } from "@web/core/utils/reactive";
import { EventBus } from "@odoo/owl";
import { rewards } from "./click_rewards";
import { choose } from "./utils";

export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.clicks = 0;
        this.level = 0;
        this.clickBotA = 0;
        this.intervalAId = "";
        this.multiplier = 1;
        this.bots = {
            botA: {
                price: 100,
                level: 1,
                increment: 10,
                purchased: 0,
            },
            botB: {
                price: 1000,
                level: 2,
                increment: 100,
                purchased: 0,
            },
        };
        this.trees = {
            pearTree: {
                price: 100000,
                level: 4,
                produce: "pear",
                purchased: 0,
            },
            cherryTree: {
                price: 100000,
                level: 4,
                produce: "cherry",
                purchased: 0,
            },
            peachTree: {
                price: 150000,
                level: 4,
                produce: "peach",
                purchased: 0,
            },
        };
        this.fruits = {
            pear: 0,
            cherry: 0,
            peach: 0,
        };
        this.bus = new EventBus();

        setInterval(() => {
            for (const bot in this.bots) {
                this.clicks +=
                    this.bots[bot].increment * this.bots[bot].purchased * this.multiplier;
            }
        }, 10000);

        setInterval(() => {
            for (const tree in this.trees) {
                this.fruits[this.trees[tree].produce] += this.trees[tree].purchased;
            }
        }, 30000);
    }

    get milestones() {
        return [
            { clicks: 100, unlock: "自動點擊機器人a型" },
            { clicks: 1000, unlock: "自動點擊機器人b型" },
            { clicks: 50000, unlock: "能源核心" },
            { clicks: 100000, unlock: "樹木系統" },
        ];
    }

    increment(inc) {
        this.clicks += inc;
        if (this.milestones[this.level] && this.clicks >= this.milestones[this.level].clicks) {
            this.bus.trigger("MILESTONE", this.milestones[this.level]);
            this.level += 1;
        }
    }

    buyBot(name) {
        if (!Object.keys(this.bots).includes(name)) {
            throw new Error(`Invalid bot name ${name}`);
        }
        if (this.clicks < this.bots[name].price) {
            return false;
        }

        this.clicks -= this.bots[name].price;
        this.bots[name].purchased += 1;
    }

    buyMultiplier() {
        if (this.clicks <= 50000) return;
        this.clicks -= 50000;
        this.multiplier++;
    }

    buyTree(name) {
        if (!Object.keys(this.trees).includes(name)) {
            throw new Error(`Invalid tree name ${name}`);
        }
        if (this.clicks < this.trees[name].price) {
            return false;
        }
        this.clicks -= this.trees[name].price;
        this.trees[name].purchased += 1;
    }

    giveReward() {
        const availableReward = [];
        for (const reward of rewards) {
            if (reward.minLevel <= this.level || !reward.minLevel) {
                if (reward.maxLevel >= this.level || !reward.maxLevel) {
                    availableReward.push(reward);
                }
            }
        }
        const reward = choose(availableReward);
        this.bus.trigger("REWARD", reward);
        return choose(availableReward);
    }

    toJSON() {
        const json = Object.assign({}, this);
        delete json["bus"];
        return json;
    }

    static fromJSON(json) {
        const clicker = new ClickerModel();
        const clickerInstance = Object.assign(clicker, json);
        return clickerInstance;
    }
}
