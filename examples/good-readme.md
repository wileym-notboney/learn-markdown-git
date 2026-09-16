# Pantry

A plain-text list of what is in the kitchen, so nobody buys a fourth jar of
cumin.

## Who this is for

Anyone who shops for this household.

## How to use it

1. Open `pantry.md`.
2. Before shopping, check the **Low** section.
3. After shopping, move items from **Low** to **Stocked**.

## Files

| File | Purpose |
|------|---------|
| [pantry.md](pantry.md) | the list itself |
| [recipes/](recipes/) | things we cook from what is here |
| [CHANGELOG.md](CHANGELOG.md) | what changed and when |

## Conventions

- One item per line.
- Quantities in brackets: `rice (2 kg)`.
- Do not delete items; move them to **Out** so we remember we once had them.

## Questions

Ask whoever last edited the file: `git log -1 -- pantry.md` tells you who.
