/** @odoo-module */

export const rewards = [
    {
        description: "500點點擊數!",
        apply(clicker) {
            clicker.increment(500);
        },
        maxLevel: 3,
    },
    {
        description: "5000點點擊數!",
        apply(clicker) {
            clicker.increment(5000);
        },
        minLevel: 3,
    },
    {
        description: "自動點擊機器人a型!",
        apply(clicker) {
            clicker.bots.botA.purchase++;
        },
        minLevel: 2,
        maxLevel: 4,
    },
    {
        description: "自動點擊機器人b型!",
        apply(clicker) {
            clicker.bots.botB.purchase++;
        },
        minLevel: 3,
    },
    {
        description: "能源核心!",
        apply(clicker) {
            clicker.multipler += 1;
        },
        minLevel: 3,
    },
];
