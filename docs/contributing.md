# Contributing Code

Hi there!

Contributions are great, but I also need to manage them as sometimes
they can create a lot of discussion and work.

If you are planning to contribute any non-trivial changes, please
reach out to me (jz) on Discord or via GitHub issues before you begin
work.  We need to be sure that your changes fit within the Lute
architecture, or make changes to the latter to support you, and I may
have ideas about directions to go with changes but haven't yet had
time to document them.

TODO - link to repo issues?

# General coding considerations

Lute has a few requirements for code:

* code must be "black formatted" (https://github.com/psf/black)
* pylint must pass
* all unit and acceptance tests pass

All of these are checked in CI and won't be relaxed.  You can check
all of these with `inv full`.

The git pre-commit hooks check black and pylint.

## Adding tests

If your change is non-trivial and not covered by the existing unit
tests, you'll need to add unit tests at the same time.

The tests are written with pytest, there are many examples in the code.

Some tests use pytest-bdd and features, which I found to be very
expressive.  If we need to create new step definitions to cover your
cases, that's pretty quick.

## Code Style

`black`.  done.

## Do One Thing

A patch or pull request should be the minimum necessary to address one issue.
Please don't make a pull request for a bunch of unrelated changes, as they are
difficult to review and will be rejected - split them up into separate
requests instead.

## Pull requests

Pull requests should go to the `develop` branch of the repository.
`lute-v3` uses "git flow" style branching, so all changes first go
into the develop branch and then are packaged for release.

## Slow PR merges hopefully never happen ...

I apologize in advance if your PR doesn't get merged in right away.
In software, there are few things are frustrating/disheartening as
putting in time and effort, and having it go nowhere.  If I don't
merge it quickly, I'll try to follow up with a comment, but ping me if
I don't.