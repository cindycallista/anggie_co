# Week 8 — IC Design EDA

**Student:** 洪英佩<br>
**Student ID:** 111211147

## What is EDA?

Electronic Design Automation (EDA) is a collection of software tools used to design and verify electronic circuits. It helps engineers move from an HDL description to a working FPGA configuration or chip layout while reducing manual errors.

```mermaid
flowchart LR
    A[RTL Design] --> B[Simulation]
    B --> C[Synthesis]
    C --> D[Place and Route]
    D --> E[Timing Check]
    E --> F[Bitstream or Chip Layout]
```

## Practical Exercise

I used the **veryl2chip web EDA** and opened the **Lesson 1: Blinky** project.

| Check | Result |
|---|---|
| RTL test (`TestBlinky`) | PASS |
| Generic-gate verification | PASS — 17 cells |
| iCE40 verification | PASS — 15 cells |
| Standard-cell verification | PASS — 17 cells |
| Virtual iCEBreaker | Flashed successfully |
| FPGA result | 33 logic cells, Fmax 33.7 MHz |

The requested clock was 12 MHz, so the reported maximum frequency of 33.7 MHz passed the timing requirement. The virtual board also showed the LEDs blinking after the bitstream was loaded.

## Observation

The same design was checked at RTL and after synthesis. Matching results at both levels show why EDA verification is important: a circuit should keep the same behavior even after it is converted into gates and device-specific cells.

## Conclusion

EDA connects coding, simulation, hardware synthesis, timing analysis, and implementation in one workflow. The exercise demonstrated how a small HDL design can be tested and turned into a working FPGA bitstream before using a physical board.

## References

- [Week 8 assignment](https://github.com/ccc115a/_co/issues/13)
- [veryl2chip](https://ccc-eda.github.io/veryl2chip/web/dist/index.html)
- [Veryl language](https://veryl-lang.org/)
