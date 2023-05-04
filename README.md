# Mafia Game

**The Mafia Game rules are based on RwinShow Mafia rules.**

## Setup and Run

### Clone

```bash
git clone --branch master https://github.com/pourya90091/Mafia-Game.git
```

### Run

```bash
python main.py
```

## Syntax

### Inputting

You can separate items in inputting with Comma (,).

- Examples:

    ```text
    Players: John, Monica, Alexander, Albert, Eva, June, Jose, Katie
    ```

    ```text
    Roles: Don, Normalmafia, Normalmafia, Doctor, Detective
    ```

## Defined Roles in the Game

>Doctor, Don, Silencer, Detective, Normalpolice, Normalmafia, Terrorist
---

## Roles Description

- ### Police Side Roles

    - #### Doctor
        >Each night, Doctor chooses a player to protect (including themself).
    - #### Silencer
        >Silencer chooses a player at night. That player is then unable to speak for the following day (also unable to voting).
    - #### Detective
        >Each night, Detective chooses a player to inquiry. Only three results can be obtained from this investigation: True, False, or No Result. This investigation resolves after any killing abilities in the Night phase.
    - #### Normalpolice
        >Normalpolice haven't special ability.

- ### Mafia Side Roles

    - #### Don
        >Each night, Don (Godfather) chooses a player to shoot.
    - #### Normalmafia
        >Normalmafia haven't special ability, just being in Mafia side.
    - #### Terrorist
        >Terrorist can assassinate one player if eliminated at day by voting.
